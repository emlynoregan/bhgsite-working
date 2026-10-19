# BHG-025 — responsive booklet reader pilot

This tool builds accessible, mobile-first **workshop prototypes** from the 38 native Publisher filtered-HTML exports. It is not a site deployer.

## Input and output

- Data: `docs/projects/bhg-site/booklet-artifacts.json` and `booklet-page-order.json`.
- Inputs are the **source copies** inside `D:\bhg-booklet-recovery-20261019\converted-html\catalogue\`. Original Meredith folders remain untouched.
- Output (local only): `D:\bhg-booklet-recovery-20261019\responsive-pilot\index.html`.
- Prototype titles: #11 Johnny Green (4 pages), #38 The Burra Cemetery Walk (26), #6 Burra Story (108).

## Running

Requires Python 3.14+ and `beautifulsoup4>=4.14`. On Dev, a private dependency copy exists under the recovery workspace's `pydeps` directory; the script detects that as a fallback. For a new machine, install from `requirements.txt` in an isolated virtual environment.

```powershell
python scripts/booklets/reader.py --ids 11 38 6
python scripts/booklets/check_pilot.py
```

The generated `book.json` is an intermediate representation, storing **original source HTML page**, numbered `PageID`, text blocks, images, positions and the heading/paragraph/table classification. Source images are copied into hashed file names under each reader's `assets/`. No content is sent to an external service.

## Text and image guarantees

- The page-order manifest comes from Publisher 16 COM, verified 626/626 source pages. We use it directly; *do not* sort the arbitrary `PageNNN.htm` filenames.
- Source fallback HTML text paragraphs are retained verbatim aside from whitespace normalization. Inline bold/italic markup is reflected in the renderer. Media references must resolve and files are copied without alteration. A previously missed semantic mortality table on Cemetery Walk page 9 is now captured (5 rows, 3 columns).
- Page sections are anchored (`#page-N`), normal-flow layout and images are responsive, with keyboard focus and a navigable page picker.
- Editorial **not yet complete**: scanned/image-only material needs transcription or carefully reviewed page-image treatment; figure alt text and caption associations are generic; heading inference, multicolumn/geometric order and selected pages need manual verification. Do not present as a fully checked edition.

## Override mechanism

An optional editable `overrides/<slug>.json` file controls specific pages. Example:

```json
{
  "pages": {
    "1": {
      "block_order": [0, 2, 1, 3],
      "kinds": {"0": "heading"},
      "image_alts": {"2": "Reviewed description of the illustration"}
    }
  }
}
```

`block_order` must be an exact permutation of all block indexes on that page; it can be omitted. The other fields use indexes **after** any rearrangement. Text itself is not silently rewritten; proposed textual corrections should be kept as separate editorial changes with clear source evidence.

## Browser tests

- Google Chrome headless desktop view: visually inspected Johnny Green.
- Chrome DevTools mobile emulation at **390 × 844**: Johnny Green, Cemetery Walk, Burra Story all had viewport width 390px and document scroll width 390px (no horizontal overflow). Rendered screenshots are in `responsive-pilot/` on Dev.
- Structural validator checks all page anchors, source-text/markup parity, image-file integrity, and table presence; writes `pilot-validation.json`.

## Publication boundary

This work is **not** deployed. The BHG Working site is itself publicly reachable. Stage/publication of the large `.pub`/PDF binaries and the modern reader needs the separate BHG-028 decision and Council/Visitor Centre consultation before promotion to Preview/Real.

Related: `docs/projects/bhg-site/booklet-working-site-plan.md`, BHG-026 catalogue/detail pages and BHG-027 full batch.

## BHG-026 — booklet index and editorial detail pages

The working site's `scripts/build.py` now calls `booklets.site.build()`, producing:

- `source/booklets/index.html`: a catalogue of all 39 entries;
- `source/booklets/<number>-<slug>/index.html`: one page for each title, including the unrecovered **The Burra Institute**;
- navigation via the site's normal `scripts/chrome.py` masthead and a homepage news item.

**Source of truth:** `docs/projects/bhg-site/booklet-artifacts.json` for titles, paths and edition metadata; `booklet-descriptions.json` for source-grounded draft write-ups. All **39 descriptions are unreviewed**. Image-heavy titles and edition differences are visibly qualified.

Run on Dev:

```powershell
python scripts/build.py
python scripts/booklets/check_site.py
```

Local tests verify 39 detail pages, 39 index links, available metadata, all local links and nav, and that **no Publisher or PDF files or links were published**. The formats are pending until BHG-028 supplies verified, approved links.

### Release guard

`scripts/publish_hou_site.py` now deliberately **refuses to upload the unapproved Booklets draft site** while `source/booklets/index.html` exists. The check runs before API auth/uploads to avoid accidentally revealing this section or its navigation. A plainly named override exists, but do not use it without BHG-028 approval.

This temporarily blocks unrelated routine site deployments from this Dev checkout while draft pages are present. Use an approved clean checkout for unrelated releases or coordinate BHG-028; do **not** bypass merely to ship other material.

HTML and generator scripts are in Git; the ~1.19 GB Publisher/PDF artifacts remain separately on Dev and are not Git-tracked or hosted. **The new section has not been deployed online.**

## BHG-027 — full locally converted set (technical completion, not editorial sign-off)

All 38 recovered titles (626 pages) now build using the deterministic page-order manifest. Output is held on Dev at `D:\bhg-booklet-recovery-20261019\responsive-full\index.html`. That local collection has 38 responsive readers, copied original images, reconstructed data tables, full-resolution image links and individually rotatable illustrations on image-heavy pages.

```powershell
python scripts/booklets/reader.py --out D:\bhg-booklet-recovery-20261019\responsive-full --all
python scripts/booklets/check_pilot.py --root D:\bhg-booklet-recovery-20261019\responsive-full --all
python scripts/booklets/check_full.py
```

The new `check_full.py` **independently parses** the native Publisher HTML, comparing source text pieces, image uses, file hashes, extracted tables, page IDs, navigation and asset links with output. Verification: **38/38 readers, 626/626 pages, 4,686 text pieces, 650 images, 16 tables**, no missing/change bytes. At true Chrome mobile/desktop viewports, **76/76 tests passed**. See `docs/projects/bhg-site/booklet-responsive-batch-report.md` and `booklet-reader-qa.json`. Install Pillow and BeautifulSoup4 from `requirements.txt`; the Dev-only Python dependency fallback is `D:\bhg-booklet-recovery-20261019\pydeps`.

**Editorial limitations**: 122 predominantly image-based pages (the entire #24/#29/#35 publications are among them), source-image text may not be searchable; source image credits, automatic heading and figure-caption ordering, multicolumn layout, selected imposed upside-down pages, and 39 draft editorial descriptions must be reviewed. Reader controls permit opening and individually rotating full-resolution illustrations without modifying them. There are two apparently blank exported pages to check against PDFs. Those review activities belong to BHG-029.

**Still local only.** This is not a command to publish. BHG-028 develops resumable asset delivery, but may not enable publicly reachable readers and original file downloads until the per-title editorial/rights review and group permission decisions are recorded.
