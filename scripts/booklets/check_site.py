#!/usr/bin/env python3
"""BHG-026 local site tests: catalogue, 39 pages and no premature binary links."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit,unquote

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    sys.path.insert(0,r"D:\bhg-booklet-recovery-20261019\pydeps")
    from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
DOCS=Path(r"C:\Users\emlyn\Documents\emlyn\docs\projects\bhg-site")
SOURCE=ROOT/"source"
def check():
    catalog=json.loads((DOCS/"booklet-artifacts.json").read_text(encoding="utf8"))["booklets"]
    editorial=json.loads((DOCS/"booklet-descriptions.json").read_text(encoding="utf8"))["booklets"]
    assert len(catalog)==len(editorial)==39
    desc={x["catalog_number"]:x for x in editorial}
    index=SOURCE/"booklets"/"index.html"
    assert index.is_file()
    content=BeautifulSoup(index.read_text(encoding="utf8"),"html.parser")
    entries=content.select(".booklet-index > .booklet-item")
    assert len(entries)==39,len(entries)
    all_pages=[index]
    for b in catalog:
        n=b["catalog_number"]
        slug=b["site_slug"] or "22-the-burra-institute"
        target=SOURCE/"booklets"/slug/"index.html"
        assert target.is_file(),(n,target)
        page=BeautifulSoup(target.read_text(encoding="utf8"),"html.parser")
        assert page.select_one("h1").get_text(strip=True)==b["title"]
        assert desc[n]["body"] in page.get_text(" ",strip=True)
        assert len(page.select(".booklet-formats"))==(b["status"]=="recovered")
        assert len(page.select("a[href$='.pub']"))==0 and len(page.select("a[href$='.pdf']"))==0
        assert not page.select('a[href*="/read/index.html"]')
        if b["status"]=="missing":
            assert "Source not yet located" in page.get_text()
        if b["listed_pages"]!=b["publisher_pages"] and b["status"]=="recovered":
            assert "edition" in page.get_text().lower()
        all_pages.append(target)
    for source in all_pages:
        soup=BeautifulSoup(source.read_text(encoding="utf8"),"html.parser")
        for link in soup.select("a[href]"):
            url=link.get("href","")
            p=urlsplit(url)
            if p.scheme or p.netloc or not p.path or p.path.startswith("/") or p.path.startswith("mailto:"):
                continue
            dest=(source.parent/unquote(p.path.replace("\\","/"))).resolve()
            assert dest.is_relative_to(SOURCE.resolve()),(source,url)
            assert dest.is_file(),(source,url,dest)
    assert not any(SOURCE.glob("booklets/**/*.pub")), "Publisher source unexpectedly staged"
    assert not any(SOURCE.glob("booklets/**/*.pdf")), "PDF binary unexpectedly staged"
    main=BeautifulSoup((SOURCE/"index.html").read_text(encoding="utf8"),"html.parser")
    assert main.select_one('a[href="booklets/index.html"]')
    assert all(BeautifulSoup(x.read_text(encoding="utf8"),"html.parser").select_one('a[href$="booklets/index.html"]')
               for x in [SOURCE/"index.html",SOURCE/"articles"/"index.html",SOURCE/"board"/"index.html"])
    print("PASS BHG-026: 39 detail pages, 39 catalogue links, 39 descriptions,"
          " all internal links resolve, site navigation present, no PDF/.pub staged or linked.")

if __name__=="__main__":
    check()
