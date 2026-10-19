"""BHG-026: generate the working site's Booklets catalogue + editorial detail pages.

Uses docs/projects/bhg-site/booklet-artifacts.json and booklet-descriptions.json.
No publication of .pub/PDF/native HTML files is done here. BHG-028 owns the gated
binary/readable-content upload and final verification.
"""
from __future__ import annotations
import html
import json
from pathlib import Path

from chrome import page, write

DOCS = Path(r"C:\Users\emlyn\Documents\emlyn\docs\projects\bhg-site")
SOURCE = Path(__file__).resolve().parents[2] / "source"
MISSING_SLUG = "22-the-burra-institute"

def esc(value):
    return html.escape(str(value), quote=True)

def load_data(docs: Path = DOCS):
    catalogue=json.loads((docs/"booklet-artifacts.json").read_text(encoding="utf-8"))["booklets"]
    descriptions=json.loads((docs/"booklet-descriptions.json").read_text(encoding="utf-8"))["booklets"]
    desc_by_id={d["catalog_number"]:d for d in descriptions}
    if len(catalogue)!=39 or len(descriptions)!=39:
        raise ValueError("39 catalogue items and 39 descriptions required")
    if len(desc_by_id)!=39 or len({b["catalog_number"] for b in catalogue})!=39:
        raise ValueError("Duplicate catalogue/descriptions IDs")
    if set(desc_by_id)!={b["catalog_number"] for b in catalogue}:
        raise ValueError("Description catalogue out of sync")
    for b in catalogue:
        d=desc_by_id[b["catalog_number"]]
        if b["title"]!=d["title"] or d["status"]!="draft_unreviewed":
            raise ValueError("Unreviewed draft mismatch")
        if not d["body"] or len(d["body"].split())<65:
            raise ValueError("Description too short")
        b["slug"]=b.get("site_slug") or MISSING_SLUG
        b["draft"]=d
        if b["status"]=="recovered" and (not b["pdf"] or not b["source_copy"] or not b["html_root"]):
            raise ValueError("Missing artifact metadata")
    return sorted(catalogue,key=lambda b:b["catalog_number"])

def status(b):
    if b["status"]=="missing":
        return "Source not yet located"
    if b["listed_pages"]!=b["publisher_pages"]:
        return "Recovered · edition/page-count check"
    return "Recovered · draft description"

def file_mb(num):
    size=num/(1024*1024)
    return f"{size:.1f} MB" if size>=1 else f"{max(1,round(size*1024))} KB"

def edition_note(b):
    if b["status"]=="missing":
        return ("This is a placeholder for a title known from the 2017 BHG booklet list. "
                "The 28-page original has not been recovered; no text or downloadable files "
                "have been invented for it.")
    if b["listed_pages"]!=b["publisher_pages"]:
        return (f"The 2017 list records {b['listed_pages']} pages; the identified Publisher "
                f"original has {b['publisher_pages']} pages. The precise edition still needs "
                "editorial confirmation.")
    return (f"The identified Publisher source has {b['publisher_pages']} pages; "
            "it matches the page count recorded in the 2017 catalogue.")

def planned_links(b):
    if b["status"]=="missing":
        return '<p class="booklet-note">No reading or download files are currently available for this title.</p>'
    # These URLs are held in the *code's route convention*, but BHG-028 must
    # actually upload files, confirm permission, and enable links only then.
    sizepub=file_mb(b["source_bytes"])
    sizepdf=file_mb(b["pdf_bytes"])
    return f"""<section class="booklet-formats" aria-label="Booklet formats">
      <h2>Formats being prepared</h2>
      <ul>
        <li><strong>Read online</strong> — responsive HTML reader. <span class="booklet-muted">In preparation · BHG-027/028</span></li>
        <li><strong>PDF</strong> — original Publisher layout, {esc(sizepdf)}. <span class="booklet-muted">Export verified; online download not enabled</span></li>
        <li><strong>Publisher original (.pub)</strong> — editable source, {esc(sizepub)}. <span class="booklet-muted">Recovered; online download not enabled</span></li>
      </ul>
      <p class="booklet-note">These files are preserved in the workshop recovery area, but the download
      links will only become active after the permissions and deployment checks in BHG-028.</p>
    </section>"""

def detail(b):
    n=b["catalog_number"];title=esc(b["title"]);slug=b["slug"]
    item_status=status(b)
    src=esc(b["draft"]["body"])
    words=b["draft"]["words"]
    warning="The draft description is based on the recovered booklet and has not yet been editorially reviewed." if b["status"]=="recovered" else "Description based on the 2017 list; original not located."
    row=f"""<dl class="booklet-facts">
      <div><dt>2017 catalogue</dt><dd>No. {n} of 39</dd></div>
      <div><dt>Format</dt><dd>{esc(b["format"])}</dd></div>
      <div><dt>Catalogue pages</dt><dd>{b["listed_pages"]}</dd></div>
      <div><dt>Recovered pages</dt><dd>{b["publisher_pages"] if b["status"]=="recovered" else "—"}</dd></div>
    </dl>"""
    body=f"""<div class="layout layout--single"><article class="paper prose booklet-detail">
       <p class="when">Burra History Group · 2017 booklet list · {esc(item_status)}</p>
       <p><a href="../index.html">← All booklets</a></p>
       <h1>{title}</h1>
       <p class="booklet-draft">{esc(warning)}</p>
       <div class="booklet-description"><p>{src}</p></div>
       {row}
       <h2>About this copy</h2>
       <p>{esc(edition_note(b))}</p>
       {planned_links(b)}
       <p class="booklet-small">Provenance, source hashes and file locations are recorded in the internal
       BHG booklet inventory. <a href="../../board/BHG-026-booklets-section/index.html">Catalogue work ticket</a>.</p>
       <p><a href="../index.html">← Back to all 39 booklets</a></p>
       </article></div>"""
    return page(title=b["title"],root="../../",extra_class="booklet-page",
                description=f"BHG workshop catalogue draft for {b['title']}.",main=body)

def index(items):
    cards=[]
    for b in items:
        summary=b["draft"]["body"].split(". ")[0].rstrip(".")+"."
        cards.append(f"""<li class="booklet-item">
          <span class="booklet-number">{b["catalog_number"]:02d}</span>
          <div><h2><a href="{esc(b["slug"])}/index.html">{esc(b["title"])}</a></h2>
          <p class="booklet-meta">{esc(b["format"])} · {b["listed_pages"]} catalogue pages · {esc(status(b))}</p>
          <p>{esc(summary)}</p></div></li>""")
    content="""<div class="layout layout--single"><article class="paper prose booklet-catalogue">
      <p class="when">Booklet collection · workshop draft · 2017 list</p>
      <h1>Burra History Group booklets</h1>
      <p>The Burra History Group's 2017 list identifies 39 locally produced booklets. Original
      Publisher files and new PDF and HTML exports have been recovered for 38 of them; the separate
      28-page <em>The Burra Institute</em> is still missing.</p>
      <p>These entries are draft descriptions for review. The downloadable Publisher and PDF
      files have been prepared, but are <strong>not yet available online</strong> pending the
      workshop's staged publication process. Responsive reading editions are in preparation.</p>
      <ol class="booklet-index">"""+"\n".join(cards)+"""</ol>
      <p>Have a copy of the missing booklet or a correction? Bring it to the group workshop.
      This list is a 2017 snapshot, not necessarily a complete record of later publications.</p>
      </article></div>"""
    return page(title="Booklets",root="../",extra_class="booklet-page",
                description="Working BHG booklet catalogue; 39 titles in the 2017 list.",
                main=content)

def build():
    items=load_data()
    write("booklets/index.html",index(items))
    for b in items:
        write(f"booklets/{b['slug']}/index.html",detail(b))
    print("Booklets generated: 39 detail pages + catalogue; no binary download links exposed.")

if __name__=="__main__":
    build()
