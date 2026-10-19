#!/usr/bin/env python3
"""Validate generated BHG-025 reader prototypes; rejects missing text/media."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    sys.path.insert(0, r"D:\bhg-booklet-recovery-20261019\pydeps")
    from bs4 import BeautifulSoup

def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()

def check(root:Path, titles:list[int]):
    data=json.loads((root/"pilot-audit.json").read_text(encoding="utf8"))
    found={row["number"]:row for row in data}
    counts={"books":0,"pages":0,"paragraphs":0,"images":0,"tables":0,"image_only":0,"missing_assets":0}
    for number in titles:
        row=found[number]
        slug=next(d.name for d in root.iterdir() if d.is_dir() and d.name.startswith(f"{number:02d}-"))
        folder=root/slug/"read"
        book=json.loads((folder/"book.json").read_text(encoding="utf8"))
        page=BeautifulSoup((folder/"index.html").read_text(encoding="utf8"),"html.parser")
        section=page.select("section.page")
        assert len(section)==row["pages"]==len(book["pages"])
        assert all(s.get("id")==f"page-{i}" for i,s in enumerate(section,1))
        assert page.find("main") and page.find("article") and page.find("meta",attrs={"name":"viewport"})
        blocks=[block for p in book["pages"] for block in p["blocks"]]
        for p in book["pages"]:
            assert p["source_html"].endswith(".htm")
            for b in p["blocks"]:
                if b["kind"] in ("heading","paragraph"):
                    visible=norm(BeautifulSoup(b["html"],"html.parser").get_text())
                    assert visible==norm(b["text"]),(number,p["page"],visible[:80],b["text"][:80])
                if b["kind"]=="image":
                    target=folder/b["path"]
                    assert target.is_file() and target.stat().st_size>0,(number,p["page"],target)
        for img in page.select("figure img"):
            assert (folder/img["src"]).is_file()
            assert img.get("alt"), (number,"image alt missing")
        assert len(page.select("figure img"))==row["image_uses"]
        assert len(page.select("section.page"))==row["pages"]
        assert (folder/"reader.css").is_file()
        counts["books"]+=1
        counts["pages"]+=len(section)
        counts["paragraphs"]+=sum(b["kind"] in ("paragraph","heading") for b in blocks)
        counts["images"]+=sum(b["kind"]=="image" for b in blocks)
        counts["tables"]+=sum(b["kind"]=="table" for b in blocks)
        counts["image_only"]+=len(row["image_only_pages"])
        print(f"PASS {number:02d}: {row['pages']} ordered pages, {row['image_uses']} images, "
              f"{sum(b['kind']=='table' for b in blocks)} data tables, "
              f"{len(row['image_only_pages'])} image-only pages")
    assert counts["books"]==len(titles)
    (root/"pilot-validation.json").write_text(json.dumps(counts,indent=2),encoding="utf8")
    print("PASS TOTAL",counts)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path(r"D:\bhg-booklet-recovery-20261019\responsive-pilot"))
    ap.add_argument("--ids",nargs="+",type=int,default=[11,38,6])
    a=ap.parse_args()
    check(a.root,a.ids)
