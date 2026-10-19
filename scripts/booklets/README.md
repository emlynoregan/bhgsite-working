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
