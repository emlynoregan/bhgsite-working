"""BHG-028 local-only tests: never touch production API or BHG public Site."""
from __future__ import annotations

import hashlib
import http.server
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import assets
import delivery


class FakeHandler(http.server.BaseHTTPRequestHandler):
    buffer: bytes = b""
    put_ct: str = ""
    def do_PUT(self):
        count = int(self.headers["Content-Length"])
        chunks = []
        while count > 0:
            data = self.rfile.read(min(10003, count))
            if not data:
                raise RuntimeError("Early request EOF")
            chunks.append(data)
            count -= len(data)
        type(self).buffer = b"".join(chunks)
        type(self).put_ct = self.headers.get("Content-Type", "")
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if not self.path.startswith("/booklets/11-johnny-green/downloads/"):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", type(self).put_ct)
        self.send_header("Content-Length", str(len(type(self).buffer)))
        self.end_headers()
        for start in range(0, len(type(self).buffer), 4096):
            self.wfile.write(type(self).buffer[start:start+4096])

    def log_message(self, *args, **kwargs):
        pass


class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(delivery.MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_integrity_and_scope(self):
        assets.validate(self.manifest)
        self.assertEqual(len(self.manifest["assets"]), 800)
        self.assertEqual(self.manifest["counts"]["pdf"], 38)
        self.assertEqual(self.manifest["counts"]["publisher"], 38)
        self.assertEqual(self.manifest["counts"]["reader"], 724)
        paths = [x["library_path"] for x in self.manifest["assets"]]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all("/booklets/" in x for x in paths))
        self.assertTrue(all("book.json" not in x for x in paths))
        self.assertTrue(all("source-copies" not in x for x in paths))
        self.assertFalse(any(p.endswith("/22-the-burra-institute/downloads/original.pub") for p in paths))

    def test_selection_and_journal_idempotence(self):
        selected = delivery.select(self.manifest,[11],["pdf","publisher","reader"])
        self.assertEqual(len(selected), 6)
        journal={"verified": {}}
        result=delivery.plan(self.manifest,selected,journal)
        self.assertEqual(result["pending"],6)
        row=selected[0]
        journal["verified"][row["library_path"]]={"sha256":row["sha256"],"size":row["size"],"public_bytes_verified":True}
        result=delivery.plan(self.manifest,selected,journal)
        self.assertEqual(result["pending"],5)
        self.assertEqual(result["previously_verified"],1)
        journal["verified"][row["library_path"]]["sha256"]="0"*64
        self.assertEqual(delivery.plan(self.manifest,selected,journal)["pending"],6)

    def test_missing_book_is_not_a_valid_target(self):
        with self.assertRaises(ValueError):
            delivery.select(self.manifest,[22],["reader"])

    def test_local_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            assets.safe_file(assets.WORKSPACE, "../other.txt")

    def test_all_public_upload_gates_fail_by_default(self):
        selected=delivery.select(self.manifest,[11],["pdf"])
        template=delivery.decisions_template(self.manifest)
        with self.assertRaises(PermissionError):
            delivery.authorise(template,selected,explicit=True)
        template["publication_authorised"]=True
        template["approval_reference"]="BHG decision 123"
        template["decision_made_by"]="BHG representative"
        with self.assertRaises(PermissionError):
            delivery.authorise(template,selected,explicit=True)
        template["approved_title_formats"]={"11":{"pdf":True}}
        with self.assertRaises(PermissionError):
            delivery.authorise(template,selected,explicit=False)
        delivery.authorise(template,selected,explicit=True)
        # No production auth or API call should be attempted if gates are false.
        with patch.object(delivery, "load_hou_config", side_effect=AssertionError("API called")):
            with self.assertRaises(PermissionError):
                delivery.execute(self.manifest,selected,{"verified":{}},
                                 delivery.decisions_template(self.manifest),confirm_publication=False)

    def test_manifest_fails_closed_on_tampering(self):
        altered=json.loads(json.dumps(self.manifest))
        altered["assets"][0]["size"] += 1
        with self.assertRaises(ValueError):
            assets.validate(altered)

    def test_upload_stream_and_full_download_digest(self):
        FakeHandler.buffer=b""
        FakeHandler.put_ct=""
        server=http.server.ThreadingHTTPServer(("127.0.0.1",0),FakeHandler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            payload=(b"Publisher test fixture\x00" * 10000)+b"tail"
            with tempfile.TemporaryDirectory() as td:
                p=Path(td)/"fixture.pdf"
                p.write_bytes(payload)
                item={
                    "library_path":"/sites/bhgsite-working/booklets/11-johnny-green/downloads/booklet.pdf",
                    "content_type":"application/pdf",
                    "size":len(payload),
                    "sha256":hashlib.sha256(payload).hexdigest(),
                }
                base=f"http://127.0.0.1:{server.server_port}"
                delivery.upload_stream(base+"/presigned-test",item,p)
                self.assertEqual(FakeHandler.buffer,payload)
                self.assertEqual(FakeHandler.put_ct,"application/pdf")
                receipt=delivery.verify_public_url(item,base=base)
                self.assertEqual(receipt["sha256"],item["sha256"])
                self.assertEqual(receipt["size"],len(payload))
                FakeHandler.buffer = FakeHandler.buffer[:-1] + b"Q"
                with self.assertRaises(RuntimeError):
                    delivery.verify_public_url(item,base=base)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
