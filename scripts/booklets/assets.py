#!/usr/bin/env python3
"""BHG-028: deterministic, local-only asset manifest for future controlled release.

No API calls or upload operations occur in this module. All inputs are copies
beneath D:\bhg-booklet-recovery-20261019; original Meredith archives untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

WORKSPACE = Path(r"D:\bhg-booklet-recovery-20261019")
DOCS = Path(r"C:\Users\emlyn\Documents\emlyn\docs\projects\bhg-site")
PREFIX = "/sites/bhgsite-working/booklets"
KINDS = {"reader", "pdf", "publisher"}
TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".pdf": "application/pdf",
    ".pub": "application/x-mspublisher",
}


def digest(path: Path) -> str:
    with path.open("rb") as src:
        return hashlib.file_digest(src, "sha256").hexdigest()


def safe_file(workspace: Path, relative: str) -> Path:
    path = (workspace / relative).resolve()
    if not path.is_relative_to(workspace.resolve()) or not path.is_file():
        raise ValueError(f"Unsafe or missing source asset: {relative}")
    return path


def generate(workspace: Path = WORKSPACE, docs: Path = DOCS) -> dict:
    source = json.loads((docs / "booklet-artifacts.json").read_text(encoding="utf-8"))
    booklets = source["booklets"]
    if len(booklets) != 39 or len([b for b in booklets if b["status"] == "recovered"]) != 38:
        raise ValueError("Expected 39 catalogue entries and 38 recovered Publisher originals")
    assets: list[dict] = []
    for b in booklets:
        if b["status"] != "recovered":
            if b["catalog_number"] != 22:
                raise ValueError("Unexpected missing booklet")
            continue
        slug = b["site_slug"]
        number = b["catalog_number"]
        paths = [
            ("pdf", b["pdf"], f"{PREFIX}/{slug}/downloads/booklet.pdf", b["pdf_sha256"], b["pdf_bytes"]),
            ("publisher", b["source_copy"], f"{PREFIX}/{slug}/downloads/original.pub", b["source_sha256"], b["source_bytes"]),
        ]
        reader = b["responsive_reader_root"]
        if not reader or not reader.endswith("/read/index.html"):
            raise ValueError(f"Reader not ready for {slug}")
        reader_root = safe_file(workspace, reader).parent
        # Deliberately EXCLUDE book.json, which contains internal Windows source paths,
        # and any validation reports, screenshots and unapproved legacy HTML exports.
        web_files = sorted([reader_root / "index.html", reader_root / "reader.css"]
                           + list((reader_root / "assets").iterdir()))
        if len(web_files) < 2 or not all(p.is_file() for p in web_files):
            raise ValueError(f"Reader asset files incomplete for {slug}")
        for path in web_files:
            rel = path.relative_to(workspace).as_posix()
            lib = f"{PREFIX}/{slug}/read/{path.relative_to(reader_root).as_posix()}"
            paths.append(("reader", rel, lib, None, None))
        for kind, rel, lib, expected_hash, expected_size in paths:
            local = safe_file(workspace, rel)
            suffix = local.suffix.lower()
            if suffix not in TYPES:
                raise ValueError(f"Unexpected asset type {rel}")
            size = local.stat().st_size
            if expected_size is not None and size != expected_size:
                raise ValueError(f"Changed source file size: {rel}")
            checksum = digest(local)
            if expected_hash is not None and checksum != expected_hash:
                raise ValueError(f"Changed source file checksum: {rel}")
            if any(x["library_path"] == lib for x in assets):
                raise ValueError(f"Duplicate remote path: {lib}")
            assets.append({
                "catalog_number": number, "kind": kind, "local_relative": rel,
                "library_path": lib, "size": size, "sha256": checksum,
                "content_type": TYPES[suffix],
            })
        print(f"MANIFEST {number:02d} {slug} ({len(paths)} assets)", flush=True)
    assets.sort(key=lambda x: (x["catalog_number"], x["kind"], x["library_path"]))
    canonical = json.dumps(assets, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    counts = Counter(a["kind"] for a in assets)
    result = {
        "schema": 1, "destination": PREFIX, "public_release_allowed": False,
        "note": "Asset manifest only. Unapproved, not uploaded; no transfer secrets or presigned URLs.",
        "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
        "counts": dict(counts), "total_bytes": sum(a["size"] for a in assets),
        "assets": assets,
    }
    assert counts["pdf"] == counts["publisher"] == 38 and counts["reader"] >= 76
    return result


def save(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def validate(manifest: dict, workspace: Path = WORKSPACE, *, verify_bytes: bool = False) -> None:
    assets = manifest["assets"]
    if len(assets) < 100 or len({x["library_path"] for x in assets}) != len(assets):
        raise ValueError("Invalid asset manifest")
    canonical = json.dumps(assets, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != manifest["manifest_sha256"]:
        raise ValueError("Manifest checksum mismatch")
    if manifest["destination"] != PREFIX or manifest["public_release_allowed"]:
        raise ValueError("Manifest has unsafe destination or release status")
    for a in assets:
        if a["kind"] not in KINDS or not a["library_path"].startswith(PREFIX + "/"):
            raise ValueError("Unknown kind / destination")
        if a["content_type"] not in TYPES.values():
            raise ValueError("Unsafe content type")
        parts = a["library_path"].split("/")
        if any(part in (".", "..") for part in parts) or "\\" in a["library_path"]:
            raise ValueError("Library path traversal")
        if a["catalog_number"] not in range(1, 40) or a["catalog_number"] == 22:
            raise ValueError("Invalid recovered catalogue number")
        if a["kind"] == "reader":
            if not a["library_path"].endswith(Path(a["local_relative"]).suffix):
                raise ValueError("Wrong asset extension")
            if "/read/" not in a["library_path"] or "/read/" not in a["local_relative"]:
                raise ValueError("Wrong reader destination")
            if a["local_relative"].endswith("/book.json"):
                raise ValueError("Internal metadata must stay private")
        elif a["kind"] == "pdf":
            if not a["library_path"].endswith("/downloads/booklet.pdf") or not a["local_relative"].lower().endswith(".pdf"):
                raise ValueError("Wrong PDF destination")
        elif a["kind"] == "publisher":
            if not a["library_path"].endswith("/downloads/original.pub") or not a["local_relative"].lower().endswith(".pub"):
                raise ValueError("Wrong Publisher destination")
        local = safe_file(workspace, a["local_relative"])
        if local.stat().st_size != a["size"]:
            raise ValueError("File size changed")
        if verify_bytes and digest(local) != a["sha256"]:
            raise ValueError("File checksum changed")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", type=Path, default=WORKSPACE)
    p.add_argument("--docs", type=Path, default=DOCS)
    p.add_argument("--output", type=Path, default=WORKSPACE / "booklet-release" / "asset-manifest.json")
    args = p.parse_args()
    m = generate(args.workspace, args.docs)
    save(args.output, m)
    print(f"READY (local only): {len(m['assets'])} assets, {m['total_bytes']:,} bytes, manifest {m['manifest_sha256']}")
