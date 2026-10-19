#!/usr/bin/env python3
"""Independent source-to-reader audit of all 38 recovered BHG booklets.

Re-parses original Publisher HTML rather than trusting the converter's counters.
Fails on dropped paragraphs, corrupted image files, invalid source page order,
missing HTML anchors/assets or lost source tables. Reports editorial exceptions.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    sys.path.insert(0,r"D:\bhg-booklet-recovery-20261019\pydeps")
    from bs4 import BeautifulSoup

def clean(s):
    return re.sub(r"\s+"," ",s.replace("\xa0"," ")).strip()

def verify(workspace:Path,docs:Path,output:Path):
    inventory={b["catalog_number"]:b for b in json.loads((docs/"booklet-artifacts.json").read_text(encoding="utf8"))["booklets"]}
    page_order=json.loads((docs/"booklet-page-order.json").read_text(encoding="utf8"))["books"]
    assert len(page_order)==38
    stats={"books":0,"pages":0,"source_paragraphs":0,"rendered_normal_paragraphs":0,"outside_table_paragraphs":0,
           "image_uses":0,"tables":0,"image_only_pages":0,"empty_source_pages":0,"byte_mismatches":0,"missing_media":0}
    detail=[]
    for entry in page_order:
        n=entry["catalog_number"]
        srcitem=inventory[n]
        slug=srcitem["site_slug"]
        native=(workspace/srcitem["html_root"]).parent
        root=output/slug/"read"
        book=json.loads((root/"book.json").read_text(encoding="utf8"))
        html=BeautifulSoup((root/"index.html").read_text(encoding="utf8"),"html.parser")
        sections=html.select("section.page")
        assert len(sections)==len(entry["pages"])==len(book["pages"])==srcitem["html_pages"],(n,"page count")
        assert len({p["page_id"] for p in book["pages"]})==len(book["pages"]),(n,"duplicate page IDs")
        imgs_in_book=0;paras=0;outs=0;tables=0;image_only=[];empties=[]
        for spec,page,section in zip(entry["pages"],book["pages"],sections):
            index=spec["page"];source=native/spec["html_file"]
            assert (page["page"],page["page_id"],page["source_html"])==(index,spec["page_id"],spec["html_file"]),(n,index,"page manifest drift")
            assert section["id"]==f"page-{index}",(n,index,"missing anchor")
            soup=BeautifulSoup(source.read_bytes().decode("cp1252"),"html.parser")
            native_paras=[clean(p.get_text("",strip=False)) for p in soup.select("div.shape p") if clean(p.get_text("",strip=False))]
            other=[p for p in soup.find_all("p") if not p.find_parent("div",class_="shape") and clean(p.get_text("",strip=False))]
            assert all(p.find_parent("table") is not None for p in other),(n,index,"unknown source paragraphs outside shapes/tables")
            expected=Counter(native_paras)
            nonparashapes=[s for s in soup.select("div.shape") if not s.find("p") and clean(s.get_text("",strip=False))]
            expected.update(clean(s.get_text("",strip=False)) for s in nonparashapes)
            actual=Counter(b["text"] for b in page["blocks"] if b["kind"] in ("heading","paragraph"))
            assert expected==actual,(n,index,"source text block mismatch",list((expected-actual).items())[:4],list((actual-expected).items())[:4])
            original_table_para=Counter(clean(p.get_text("",strip=False)) for p in other)
            output_tables=[b for b in page["blocks"] if b["kind"]=="table"]
            if other:assert output_tables,(n,index,"table absent")
            # Some Publisher pages have TWO or more distinct data tables.
            # Check coverage against their union, not every table separately.
            joined=" ".join(str(cell) for b in output_tables for row in b["rows"] for cell in row)
            for paragraph in original_table_para:
                assert paragraph in joined,(n,index,"table text dropped",paragraph[:80])
            tables+=len(output_tables)
            media=[x.get("src","") for x in soup.find_all("img")]
            emitted=[b for b in page["blocks"] if b["kind"]=="image"]
            assert Counter(media)==Counter(b["src"] for b in emitted),(n,index,"media-use mismatch")
            assert len(section.select("figure img"))==len(media),(n,index,"HTML image count")
            for figure in section.select("figure.reader-figure"):
                image=figure.select_one("img")
                link=figure.select_one("a.full-image")
                assert image and link and link.get("href")==image.get("src"),(n,index,"full-size image link")
                assert image.get("width") and image.get("height"),(n,index,"missing image dimensions")
                if page["image_only"]:
                    assert figure.select_one("input.image-flip") and figure.select_one("label.image-flip-label"),(n,index,"missing image rotation control")
            for b in emitted:
                original=(source.parent/b["src"].replace("\\","/")).resolve()
                generated=root/b["path"]
                assert original.is_relative_to(native.resolve()),(n,index,"image escaped root")
                assert original.is_file() and generated.is_file(),(n,index,"missing asset")
                with original.open("rb") as f1,generated.open("rb") as f2:
                    assert hashlib.file_digest(f1,"sha256").digest()==hashlib.file_digest(f2,"sha256").digest(),(n,index,"image bytes changed")
            for block in page["blocks"]:
                if block["kind"] in ("paragraph","heading"):
                    recovered=clean(BeautifulSoup(block["html"],"html.parser").get_text())
                    assert recovered==clean(block["text"]),(n,index,"rich HTML text drift")
            if page["image_only"]:image_only.append(index)
            if not page["blocks"]:empties.append(index)
            imgs_in_book+=len(media)
            paras+=len(native_paras)+len(nonparashapes)
            outs+=len(other)
        # Check the emitted links and anchors without making network requests.
        anchors={v.get("id") for v in html.find_all(id=True)}
        for a in html.select("a[href]"):
            href=a["href"]
            if href.startswith("#"):
                assert href[1:] in anchors,(n,"invalid page anchor",href)
            elif href.startswith("../../"):
                assert (root/href).resolve().is_file(),(n,"missing local link",href)
        note={"catalog_number":n,"title":srcitem["title"],"slug":slug,
              "technical_status":"verified_source_fidelity_editorial_review_pending",
              "reader_root":f"responsive-full/{slug}/read/index.html",
              "source_pages":len(entry["pages"]), "shape_text_paragraphs":paras,
              "outside_table_paragraphs":outs,"image_uses":imgs_in_book,
              "tables":tables-stats["tables"],"image_only_pages":image_only,"empty_pages":empties,
              "review_needed":bool(image_only or outs),"description":"Reader contains source text and images; complex layout/caption/alt review required"}
        # Estimate tables on this title directly (independent of other book totals)
        note["tables"]=sum(b["kind"]=="table" for p in book["pages"] for b in p["blocks"])
        detail.append(note)
        stats["books"]+=1
        stats["pages"]+=len(book["pages"])
        stats["source_paragraphs"]+=paras+outs
        stats["rendered_normal_paragraphs"]+=paras
        stats["outside_table_paragraphs"]+=outs
        stats["image_uses"]+=imgs_in_book
        stats["tables"]+=note["tables"]
        stats["image_only_pages"]+=len(image_only)
        stats["empty_source_pages"]+=len(empties)
        print(f"PASS {n:02d} {len(entry['pages'])} pages {paras}+{outs} source paragraphs {imgs_in_book} images {note['tables']} tables, {len(image_only)} image-based",flush=True)
    assert stats["books"]==38 and stats["pages"]==626 and stats["image_uses"]==650 and stats["outside_table_paragraphs"]==448,(stats,"preflight parity")
    report={"version":1,"release_status":"local conversion verified, NOT publication approved",
            "summary":stats,"booklets":detail,
            "limitations":["Image-only/source-imposed pages are not automatically searchable or all correctly oriented",
                "Page-internal visual reading order, captions, alt text and artwork credits require editorial review",
                "Original physical PDF/Publisher layout remains authoritative",
                "No files approved for public online hosting by this QA alone"]}
    (output/"full-validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
    print("SUCCESS",stats)
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--workspace",type=Path,default=Path(r"D:\bhg-booklet-recovery-20261019"))
    parser.add_argument("--docs",type=Path,default=Path(r"C:\Users\emlyn\Documents\emlyn\docs\projects\bhg-site"))
    parser.add_argument("--out",type=Path,default=Path(r"D:\bhg-booklet-recovery-20261019\responsive-full"))
    a=parser.parse_args();verify(a.workspace,a.docs,a.out)
