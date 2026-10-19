#!/usr/bin/env python3
"""BHG-025: semantic, responsive reader pilot from Publisher HTML.

Run: python scripts/booklets/reader.py --ids 11 38 6
Requires BeautifulSoup4. Does NOT change source files or publish to House Sites.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

try:
    from bs4 import BeautifulSoup, NavigableString, Tag
except ModuleNotFoundError:
    sys.path.insert(0, r"D:\bhg-booklet-recovery-20261019\pydeps")
    from bs4 import BeautifulSoup, NavigableString, Tag

try:
    from PIL import Image
except ModuleNotFoundError:
    sys.path.insert(0, r"D:\bhg-booklet-recovery-20261019\pydeps")
    from PIL import Image

SPACE = re.compile(r"\s+")
POSITION = re.compile(r"(left|top|width|height)\s*:\s*(-?\d+(?:\.\d+)?)px", re.I)
IMAGES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

def clean(text):
    return SPACE.sub(" ", text.replace("\xa0", " ")).strip()

def coords(element):
    while isinstance(element, Tag):
        style=element.get("style", "")
        if "position:absolute" in style.replace(" ", "").lower():
            result={key.lower():float(val) for key,val in POSITION.findall(style)}
            if "top" in result:
                return result
        element=element.parent
    return {}

def rich(node):
    if isinstance(node, NavigableString):
        return html.escape(str(node).replace("\xa0", " "))
    if not isinstance(node, Tag):
        return ""
    body="".join(rich(child) for child in node.children)
    style=node.get("style", "").lower()
    tag=node.name.lower()
    if tag in ("em","i") or "font-style:italic" in style:
        body="<em>"+body+"</em>"
    if tag in ("strong","b") or re.search(r"font-weight:(bold|[6-9]00)",style):
        body="<strong>"+body+"</strong>"
    if tag in ("sup","sub"):
        body=f"<{tag}>{body}</{tag}>"
    if tag=="br":
        return " "
    return body

def is_heading(p, text):
    if len(text)>100 or len(text.split())>14:
        return False
    css=" ".join([p.get("style","")]+[x.get("style","") for x in p.find_all(["span","strong","b"])])
    return bool(re.search(r"font-weight\s*:\s*(bold|[6-9]00)",css,re.I) or p.find(["strong","b"]))

def extract(root:Path, source:Path, assets:Path, inventory:dict):
    soup=BeautifulSoup(source.read_bytes().decode("cp1252"),"html.parser")
    blocks=[]
    para_source=[]
    imgs=[]
    for shape in soup.select("div.shape"):
        where=coords(shape)
        paras=shape.find_all("p")
        if not paras and clean(shape.get_text("",strip=False)):
            text=clean(shape.get_text("",strip=False))
            blocks.append(dict(kind="paragraph",text=text,html=html.escape(text),pos=where))
            para_source.append(text)
        for para in paras:
            text=clean(para.get_text("",strip=False))
            if not text:
                continue
            body=clean("".join(rich(part) for part in para.children))
            blocks.append(dict(kind="heading" if is_heading(para,text) else "paragraph",
                               text=text,html=body,pos=where))
            para_source.append(text)
    # A few Publisher data tables live outside the normal text-shape fallback.
    # Capture those cells as genuine semantic tables, not just their raster overlays.
    outside=[p for p in soup.find_all("p") if p.find_parent("div",class_="shape") is None
             and clean(p.get_text("",strip=False))]
    accounted=[]
    for table in soup.find_all("table"):
        missing=[p for p in table.find_all("p") if p in outside]
        if not missing:
            continue
        # Layout tables wrapping a normal Publisher text box are not data tables.
        rows=[]
        for tr in table.find_all("tr"):
            cells=[]
            for cell in tr.find_all(["td","th"],recursive=False):
                txt=clean(cell.get_text("",strip=False))
                cells.append(txt)
                for para in cell.find_all("p"):
                    if para in outside:
                        accounted.append(para)
                        para_source.append(clean(para.get_text("",strip=False)))
            if cells:rows.append(cells)
        if rows:
            blocks.append(dict(kind="table",rows=rows,pos=coords(table),
                               text=" | ".join(" | ".join(row) for row in rows)))
    if Counter(id(p) for p in accounted)!=Counter(id(p) for p in outside):
        raise ValueError(f"Uncaptured paragraphs outside Publisher shapes: {source}")
    for image in soup.find_all("img"):
        name=image.get("src")
        if not name:
            continue
        path=(source.parent/name.replace("\\","/")).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"Missing/escaped source picture {name} in {source}")
        if path.suffix.lower() not in IMAGES:
            raise ValueError(f"Unsupported source picture {name}")
        digest=hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        dest=f"{digest}-{path.name}"
        if not (assets/dest).exists():
            shutil.copy2(path,assets/dest)
        inventory[dest]=str(path)
        imgs.append(name)
        # Explicit natural dimensions reserve layout space before lazy images load,
        # preventing #page-N anchors from shifting while reading.
        with Image.open(path) as original_image:
            natural_width,natural_height=original_image.size
        if natural_width<=0 or natural_height<=0:
            raise ValueError(f"Invalid image dimensions: {path}")
        blocks.append(dict(kind="image",path=f"assets/{dest}",src=name,pos=coords(image),
                           width=natural_width,height=natural_height))
    # Geometry orders shapes; inside each text shape the original paragraph order survives.
    for i,b in enumerate(blocks):
        b["_ordinal"]=i
    blocks.sort(key=lambda b:(b["pos"].get("top",99999),b["pos"].get("left",0),b["_ordinal"]))
    for b in blocks:del b["_ordinal"]
    extracted=[b["text"] for b in blocks if b["kind"] in ("heading","paragraph")]
    extracted+= [clean(p.get_text("",strip=False)) for p in outside]
    if Counter(extracted)!=Counter(para_source):
        raise ValueError(f"Text loss/duplication {source}")
    if sum(b["kind"]=="image" for b in blocks)!=len(imgs):
        raise ValueError(f"Image mismatch {source}")
    return dict(source_html=source.relative_to(root).as_posix(),blocks=blocks,
                paragraphs=len(para_source),images=len(imgs),
                image_only=bool(imgs) and not any(len(x)>35 for x in extracted),
                empty=not blocks)

def apply_overrides(page: dict, spec: dict) -> None:
    """Optional, reviewable manual corrections, by source page and block index."""
    if not spec:
        return
    blocks=page["blocks"]
    order=spec.get("block_order")
    if order is not None:
        if sorted(order)!=list(range(len(blocks))):
            raise ValueError(f"Invalid block_order for page {page['page']}")
        page["blocks"]=[blocks[i] for i in order]
        blocks=page["blocks"]
    for index,kind in spec.get("kinds",{}).items():
        b=blocks[int(index)]
        if b["kind"] not in ("heading","paragraph") or kind not in ("heading","paragraph"):
            raise ValueError(f"Unsupported kind override at {page['page']}:{index}")
        b["kind"]=kind
    for index,alt in spec.get("image_alts",{}).items():
        b=blocks[int(index)]
        if b["kind"]!="image" or not isinstance(alt,str) or not alt.strip():
            raise ValueError(f"Invalid image alt override for {page['page']}:{index}")
        b["alt"]=alt.strip()


def render(book):
    esc=html.escape
    title=esc(book["title"])
    result=['<!doctype html><html lang="en-AU"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            f'<title>{title} — BHG booklet reader</title>',
            '<link rel="stylesheet" href="reader.css"></head><body>',
            '<header class="mast"><p class="kicker">Burra History Group · working reader prototype</p>',
            f'<h1>{title}</h1>',
            '<p>Responsive adaptation of an original Publisher booklet. Page references are retained. ',
            'For the original print layout, consult the source PDF.</p></header>',
            '<main class="content"><nav class="tools" aria-label="Reader controls">',
            f'<span>{len(book["pages"])} source pages</span><a href="../../index.html">Pilot collection</a>',
            '<details><summary>Jump to page</summary><ol>']
    for p in book["pages"]:
        num=p["page"]
        result.append(f'<li><a href="#page-{num}">Page {num}</a></li>')
    result.extend(['</ol></details></nav><article class="book">'])
    for p in book["pages"]:
        num=p["page"]
        result.append(f'<section class="page" id="page-{num}" aria-label="Page {num}">')
        result.append(f'<header class="pagehead"><span>Page {num} of {len(book["pages"])}</span>'
                      '<a href="#page-1">Back to top</a></header>')
        result.append('<div class="prose">')
        for idx,b in enumerate(p["blocks"]):
            if b["kind"]=="image":
                alt=esc(b.get("alt") or f"Illustration on original booklet page {num}, description pending editorial review.",quote=True)
                src=esc(b["path"],quote=True)
                result.append('<figure class="reader-figure">')
                if p["image_only"]:
                    fid=f"flip-{num}-{idx}"
                    result.append(f'<input class="image-flip" type="checkbox" id="{fid}">'
                                  f'<label class="image-flip-label" for="{fid}">Rotate this image 180°</label>')
                result.append(f'<a class="full-image" href="{src}" target="_blank" rel="noopener" '
                              f'aria-label="Open original illustration from page {num} at full resolution">'
                              f'<img loading="lazy" decoding="async" width="{b["width"]}" height="{b["height"]}" '
                              f'src="{src}" alt="{alt}"></a>'
                              f'<figcaption>Illustration from original page {num}.</figcaption></figure>')
            elif b["kind"]=="heading":
                result.append(f'<h2>{b["html"]}</h2>')
            elif b["kind"]=="table":
                result.append('<div class="table-scroll" role="region" aria-label="Original booklet table" tabindex="0"><table>')
                for ri,row in enumerate(b["rows"]):
                    result.append('<tr>')
                    for cell in row:
                        t="th" if ri==0 else "td"
                        scope=' scope="col"' if ri==0 else ""
                        result.append(f'<{t}{scope}>{html.escape(cell)}</{t}>')
                    result.append('</tr>')
                result.append('</table></div>')
            else:
                result.append(f'<p>{b["html"]}</p>')
        if not p["blocks"]:
            result.append('<p class="empty">This source page has no extractable content.</p>')
        result.append('</div></section>')
    result.extend(['</article><footer>Working conversion prototype — not an edited or definitive publication. '
                   'Caption associations, scanned text and alt descriptions need editorial review. '
                   'The original Publisher sources have not been modified.</footer></main></body></html>'])
    return "\n".join(result)

CSS = """
:root{--ink:#26352f;--accent:#0e594c;--paper:#fffcf5;--ground:#f1efe8;--line:#d5d9d2}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--ground);color:var(--ink);font:clamp(1rem,.45vw + .95rem,1.15rem)/1.7 Georgia,serif}
a{color:var(--accent);text-underline-offset:.16em}
a:focus-visible{outline:3px solid #cc9d54;outline-offset:3px}
.mast{background:#263f35;color:#fff;padding:1.7rem max(1rem,calc((100vw - 1000px)/2))}
.mast h1{font:600 clamp(1.65rem,3.8vw,2.8rem)/1.2 Georgia,serif;margin:.25rem 0 1rem}
.mast .kicker{font:600 .8rem/1.5 system-ui,sans-serif;letter-spacing:.09em;text-transform:uppercase;color:#d9e3d5}
.mast p{max-width:70ch;font:400 .92rem/1.6 system-ui,sans-serif;color:#e2e9e0}
.content{max-width:1030px;margin:auto;padding:clamp(.5rem,2vw,2rem)}
.tools{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin:.8rem auto 1.25rem;padding:0 1rem;font:500 .87rem/1.5 system-ui,sans-serif;max-width:840px}
.tools details{margin-left:auto}.tools summary{cursor:pointer}.tools ol{columns:3;max-height:18rem;overflow:auto;padding-left:1.5rem}
.book{max-width:840px;margin:auto}
.page{margin-bottom:1.5rem;background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:clamp(1rem,4.5vw,3.4rem);overflow-wrap:break-word;box-shadow:0 2px 12px #1329200e}
.page:target{outline:2px solid #ac935a}
.pagehead{border-bottom:1px solid var(--line);padding:0 0 .7rem;margin:0 0 1.3rem;display:flex;justify-content:space-between;gap:.5rem;color:#647069;font:500 .78rem/1.35 system-ui,sans-serif}
.prose{max-width:69ch;margin:auto}.prose p{margin:0 0 1em}
.prose h2{font:600 clamp(1.25rem,2.2vw,1.75rem)/1.3 Georgia,serif;color:#1c4536;margin:1.4rem 0 .8rem}
figure{margin:1.45rem auto;text-align:center;max-width:100%}
.reader-figure a{display:inline-block;max-width:100%;cursor:zoom-in}
.image-flip{margin-right:.35rem}
.image-flip-label{display:inline-block;cursor:pointer;color:#596961;font:500 .78rem/1.5 system-ui,sans-serif;margin-bottom:.5rem}
.image-flip:checked ~ a img{transform:rotate(180deg)}
figure img{display:block;max-width:100%;height:auto;object-fit:contain;margin:auto;box-shadow:0 1px 8px #14281b20}
figcaption{font:.83rem/1.5 system-ui,sans-serif;color:#65716b;padding:.4rem 0}
.table-scroll{overflow-x:auto;max-width:100%;margin:1.4rem 0}
.table-scroll table{border-collapse:collapse;width:100%;font:.92rem/1.5 system-ui,sans-serif}
.table-scroll td,.table-scroll th{text-align:left;padding:.55rem .7rem;border:1px solid var(--line)}
.table-scroll th{background:#e3e9e1}
footer{max-width:69ch;margin:2rem auto;padding:1.5rem 0 3rem;border-top:1px solid var(--line);font:.86rem/1.5 system-ui,sans-serif;color:#5d6860}
@media(max-width:600px){.content{padding:.5rem 0}.page{border-radius:0;padding:1rem}.tools details{margin-left:0}}
@media print{body{background:white}.mast,.tools{display:none}.page{border:0;box-shadow:none;break-inside:avoid}.pagehead a{display:none}}
"""

def convert(workspace,docs,out,ids):
    data=json.loads((docs/"booklet-artifacts.json").read_text(encoding="utf-8"))
    ordered=json.loads((docs/"booklet-page-order.json").read_text(encoding="utf-8"))
    files={b["catalog_number"]:b for b in data["booklets"]}
    pages={b["catalog_number"]:b["pages"] for b in ordered["books"]}
    out.mkdir(parents=True,exist_ok=True)
    report=[]
    for n in ids:
        item=files[n]
        if item["status"]!="recovered":raise ValueError(f"No source for #{n}")
        slug=item["site_slug"]
        pub=workspace/item["source_copy"]
        with pub.open("rb") as source_handle:
            actual_hash=hashlib.file_digest(source_handle,"sha256").hexdigest()
        if actual_hash!=item["source_sha256"]:
            raise ValueError(f"Publisher source changed since recovery: {pub}")
        correction_file=Path(__file__).parent/"overrides"/(slug+".json")
        corrections=json.loads(correction_file.read_text(encoding="utf-8")) if correction_file.exists() else {}
        original=(workspace/item["html_root"]).parent
        dest=out/slug/"read"
        (dest/"assets").mkdir(parents=True,exist_ok=True)
        assets={}
        book=dict(number=n,title=item["title"],slug=slug,pages=[])
        if len(pages[n])!=item["html_pages"]:raise ValueError("Page count changed")
        for row in pages[n]:
            source=original/row["html_file"]
            if not source.is_file():raise FileNotFoundError(source)
            pg=extract(original,source,dest/"assets",assets)
            pg.update(page=row["page"],page_id=row["page_id"])
            apply_overrides(pg,corrections.get("pages",{}).get(str(row["page"]),{}))
            book["pages"].append(pg)
        (dest/"index.html").write_text(render(book),encoding="utf-8")
        (dest/"reader.css").write_text(CSS,encoding="utf-8")
        (dest/"book.json").write_text(json.dumps(book,ensure_ascii=False,indent=2),encoding="utf-8")
        imgs=sum(p["images"] for p in book["pages"])
        txt=sum(p["paragraphs"] for p in book["pages"])
        image_only=[p["page"] for p in book["pages"] if p["image_only"]]
        result=dict(number=n,title=item["title"],pages=len(book["pages"]),paragraphs=txt,
                    image_uses=imgs,unique_images=len(assets),image_only_pages=image_only,
                    status="needs_visual_and_editorial_review")
        report.append(result)
        print(f"{n}: {result['pages']} pages; {txt} text blocks; {imgs} images; image-only {len(image_only)}",flush=True)
    (out/"pilot-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    links="\n".join(f'<li><a href="{files[b["number"]]["site_slug"]}/read/index.html">{html.escape(b["title"])}</a>'
                    f' — {b["pages"]} pages</li>' for b in report)
    (out/"index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1"><title>BHG reader pilot</title>'
      '<style>body{font:18px/1.6 system-ui,sans-serif;max-width:70ch;margin:3rem auto;padding:0 1rem}</style>'
      '<h1>BHG responsive reader pilots</h1><p>Local previews only. Editorial review pending.</p>'
      '<ul>'+links+'</ul></html>',encoding="utf-8")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--workspace",type=Path,default=Path(r"D:\bhg-booklet-recovery-20261019"))
    p.add_argument("--docs",type=Path,default=Path(r"C:\Users\emlyn\Documents\emlyn\docs\projects\bhg-site"))
    p.add_argument("--out",type=Path,default=Path(r"D:\bhg-booklet-recovery-20261019\responsive-pilot"))
    p.add_argument("--ids",type=int,nargs="+",default=[11,38,6])
    p.add_argument("--all",action="store_true",help="Convert all 38 recovered items from the manifest")
    a=p.parse_args()
    if a.all:
        manifest=json.loads((a.docs/"booklet-artifacts.json").read_text(encoding="utf8"))
        a.ids=[b["catalog_number"] for b in manifest["booklets"] if b["status"]=="recovered"]
    convert(a.workspace,a.docs,a.out,a.ids)
