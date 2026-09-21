"""Wrap converted markdown (or HTML fragments) in the working-site chrome."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"


def page(
    *,
    title: str,
    root: str,
    main: str,
    extra_class: str = "",
    description: str = "Working notes for the Burra History Group public website rebuild.",
) -> str:
    css = f"{root}css/working.css"
    body_class = f' class="{extra_class}"' if extra_class else ""
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — BHG Site Working</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="{css}">
</head>
<body{body_class}>
  <header class="mast">
    <p class="mast__kicker"><a href="{root}index.html">BHG Site Working</a></p>
    <p class="mast__tag">Rebuild workshop — not the public history site</p>
    <nav class="mast__nav" aria-label="Working site">
      <a href="{root}index.html">News</a>
      <a href="{root}meetings/index.html">Meetings</a>
      <a href="{root}board/index.html">Todo</a>
      <a href="{root}articles/index.html">Articles</a>
      <a href="{root}process/index.html">Process</a>
      <a href="{root}glossary/index.html">Glossary</a>
    </nav>
    <p class="mast__elsewhere">Public site:
      <a href="https://preview1845-bhg.house-of-ur.com/">Preview</a> ·
      <a href="https://real-bhg.house-of-ur.com/">Real</a> ·
      <a href="https://burrasa.net">burrasa.net</a> (live until cutover)
    </p>
    <p class="mast__elsewhere">Prototypes:
      <a href="https://emlynoregan.com/bitn/" target="_blank" rel="noopener">Burra in the News</a> ·
      <a href="https://bda-dev.emlynoregan.com/" target="_blank" rel="noopener">Burra Digital Archive</a>
    </p>
  </header>
  {main}
  <footer class="foot">
    <p>Burra History Group · House of Ur · working notes for <code>bhgsite2026</code></p>
  </footer>
</body>
</html>
"""


def write(rel: str, html: str) -> None:
    dest = SOURCE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    print(f"wrote {dest.relative_to(ROOT)}")
