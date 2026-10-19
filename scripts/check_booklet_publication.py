#!/usr/bin/env python3
"""BHG-028: public Working-site smoke test; GET HTML and HEAD binaries.

This script never writes to House. Its 38 binary checks verify response headers;
full SHA-256 readbacks are done by delivery.py before recording receipts.
"""
import argparse
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

from booklets.release import ready
from booklets.assets import DOCS,WORKSPACE

SITE="https://working-bhg.house-of-ur.com"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"Cache-Control":"no-cache"}),timeout=90) as r:
        return r.status,r.headers.get("Content-Type",""),r.read()

def head(url):
    with urllib.request.urlopen(urllib.request.Request(url,method="HEAD",headers={"Cache-Control":"no-cache"}),timeout=60) as r:
        return r.status,r.headers.get("Content-Type",""),r.headers.get("Content-Length"),r.headers.get("Content-Disposition")

def check():
    ok, reason=ready()
    if not ok:
        raise RuntimeError("Not ready for public smoke checks: "+reason)
    catalog=json.loads((DOCS/"booklet-artifacts.json").read_text(encoding="utf8"))["booklets"]
    status,typ,main=get(SITE+"/index.html")
    assert status==200 and b"booklets/index.html" in main
    status,typ,index=get(SITE+"/booklets/index.html")
    assert status==200 and b"Burra History Group booklets" in index
    all_urls=[]
    for b in catalog:
        slug=b["site_slug"] or "22-the-burra-institute"
        detail_url=f"{SITE}/booklets/{slug}/index.html"
        all_urls.append(("detail",b,detail_url))
        if b["status"]=="recovered":
            all_urls.append(("reader",b,f"{SITE}/booklets/{slug}/read/index.html"))
            all_urls.append(("pdf",b,f"{SITE}/booklets/{slug}/downloads/booklet.pdf"))
            all_urls.append(("publisher",b,f"{SITE}/booklets/{slug}/downloads/original.pub"))
    errors=[]
    def test(x):
        kind,b,url=x
        if kind in ("detail","reader"):
            status,typ,data=get(url)
            if status!=200 or not typ.startswith("text/html"):
                raise RuntimeError(f"{kind} content type: {typ}")
            if kind=="detail":
                for rel in (["read/index.html","downloads/booklet.pdf","downloads/original.pub"] if b["status"]=="recovered" else []):
                    if rel.encode() not in data:
                        raise RuntimeError(f"detail missing {rel}")
                if b"draft" not in data.lower() and b"review" not in data.lower():
                    raise RuntimeError("Editorial review caveat absent")
            else:
                if b"Source page" not in data and b"Page 1 of" not in data:
                    raise RuntimeError("Reader page references absent")
            return kind
        status,typ,length,disp=head(url)
        expect="application/pdf" if kind=="pdf" else "application/x-mspublisher"
        expected_len=b["pdf_bytes"] if kind=="pdf" else b["source_bytes"]
        if status!=200 or not typ.startswith(expect) or (length is not None and int(length)!=expected_len):
            raise RuntimeError(f"bad {kind}: status={status} type={typ} length={length}")
        return kind
    counts={}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures={pool.submit(test,x):x for x in all_urls}
        for f in as_completed(futures):
            x=futures[f]
            try:
                k=f.result();counts[k]=counts.get(k,0)+1
            except Exception as exc:
                errors.append(f"{x[0]} title {x[1]['catalog_number']}: {type(exc).__name__} {exc}")
    print("LIVE CHECKS",counts,"ERRORS",len(errors),flush=True)
    for e in errors:print("FAIL",e,flush=True)
    if errors:raise RuntimeError(f"{len(errors)} live checks failed")
    assert counts=={"detail":39,"reader":38,"pdf":38,"publisher":38},counts
    print("SUCCESS: Working site catalogue, 39 details, 38 readers, 76 downloads; Preview/Real not touched.")


if __name__=="__main__":
    check()
