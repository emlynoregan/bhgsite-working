"""Import Preview Feature HTML into the workshop Articles section."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORT = ROOT / "import" / "features"
WORKING_SOURCE = ROOT / "source"
PREVIEW = "https://preview1845-bhg.house-of-ur.com"


def inner_article(html: str) -> str:
    match = re.search(r'<article class="document"[^>]*>(.*)</article>', html, re.S)
    if not match:
        raise ValueError("no article.document in feature HTML")
    body = match.group(1)
    body = re.sub(r'<footer class="site-footer">.*?</footer>', "", body, flags=re.S)
    return body.strip()


def apply(html: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        html = html.replace(old, new)
    return html


def site_root_pairs() -> list[tuple[str, str]]:
    """Longest-first replacements for pages whose data-root was ../../ (Feature article)."""
    return [
        ("../../features/creek-street/", "../creek-street/index.html"),
        ("../../features/trees/", "../trees/index.html"),
        ("../../features/johnny-green/", "../johnny-green/index.html"),
        ("../../places/", f"{PREVIEW}/places/"),
        ("../../mine/timeline/", f"{PREVIEW}/mine/timeline/"),
        ("../../mine/smelting/", f"{PREVIEW}/mine/smelting/"),
        ("../../town/timeline/", f"{PREVIEW}/town/timeline/"),
        ("../../town/townships-map/", f"{PREVIEW}/town/townships-map/"),
        ("../../resources/", f"{PREVIEW}/resources/"),
        ("../../genealogy/notables/", f"{PREVIEW}/genealogy/notables/"),
        ("../../genealogy/", f"{PREVIEW}/genealogy/"),
        ("../../contact/", f"{PREVIEW}/contact/"),
        ("../../town/", f"{PREVIEW}/town/"),
        ("../../mine/", f"{PREVIEW}/mine/"),
        ("../../map/", f"{PREVIEW}/map/"),
    ]


def copy_images(src_dir: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in src_dir.iterdir():
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
            shutil.copy2(path, dest_dir / path.name)


def write_imported_features(write, paper) -> None:
    copy_images(IMPORT / "johnny-green", WORKING_SOURCE / "articles/johnny-green/article")
    copy_images(IMPORT / "creek-street", WORKING_SOURCE / "articles/creek-street")

    johnny = inner_article((IMPORT / "johnny-green/index.html").read_text(encoding="utf-8"))
    johnny = apply(
        johnny,
        [
            (
                '<p class="crumbs"><a href="../">Features</a></p>',
                '<p class="crumbs"><a href="../../index.html">Articles</a> · <a href="../index.html">Johnny Green</a></p>',
            ),
            ('href="jenner-note/"', 'href="../research/jenner-note/index.html"'),
            ('href="bhg-booklet-2008/"', 'href="../research/bhg-booklet-2008/index.html"'),
            ('href="national-trust-notes/"', 'href="../research/national-trust-notes/index.html"'),
        ]
        + site_root_pairs(),
    )
    write(
        "articles/johnny-green/article/index.html",
        paper("Johnny Green: Mascot of the Burra Miners", "../../../", johnny, extra_class="imported-feature"),
    )

    for slug, title in (
        ("jenner-note", "Jenner family note on Johnny Green, 1960"),
        ("bhg-booklet-2008", "Johnny Green booklet, 2008"),
        ("national-trust-notes", "Burra National Trust notes on Johnny Green"),
    ):
        body = inner_article((IMPORT / "johnny-green" / slug / "index.html").read_text(encoding="utf-8"))
        body = apply(
            body,
            [
                (
                    '<p class="crumbs"><a href="../../">Features</a> · <a href="../">Johnny Green</a></p>',
                    '<p class="crumbs"><a href="../../../index.html">Articles</a> · <a href="../../index.html">Johnny Green</a></p>',
                ),
                ('href="../"', 'href="../../article/index.html"'),
                ('src="../05-minespa-johnny-silhouette.jpg"', 'src="../../article/05-minespa-johnny-silhouette.jpg"'),
                ("../../../resources/", f"{PREVIEW}/resources/"),
                ("../../../contact/", f"{PREVIEW}/contact/"),
            ],
        )
        write(
            f"articles/johnny-green/research/{slug}/index.html",
            paper(title, "../../../../", body, extra_class="imported-feature"),
        )

    creek = inner_article((IMPORT / "creek-street/index.html").read_text(encoding="utf-8"))
    creek = apply(
        creek,
        [
            (
                '<p class="crumbs"><a href="../">Features</a></p>',
                '<p class="crumbs"><a href="../index.html">Articles</a></p>',
            ),
        ]
        + site_root_pairs(),
    )
    write(
        "articles/creek-street/index.html",
        paper("Creek Street: Life and Death in the Burra Dugouts", "../../", creek, extra_class="imported-feature"),
    )

    trees = inner_article((IMPORT / "trees/index.html").read_text(encoding="utf-8"))
    trees = apply(
        trees,
        [
            (
                '<p class="crumbs"><a href="../">Features</a></p>',
                '<p class="crumbs"><a href="../index.html">Articles</a></p>',
            ),
        ]
        + site_root_pairs(),
    )
    write(
        "articles/trees/index.html",
        paper("The Trees of Burra: From Treeless Plains to Garden Town", "../../", trees, extra_class="imported-feature"),
    )
