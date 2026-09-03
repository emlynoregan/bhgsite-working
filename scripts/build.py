"""Build BHG Site Working HTML under source/."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chrome import page, write  # noqa: E402
from mdhtml import convert  # noqa: E402

DOCS = Path(r"C:\Users\emlyn\Documents\emlyn\docs\projects\bhg-site")


def md(path: Path, *, replacements: list[tuple[str, str]] | None = None) -> str:
    text = path.read_text(encoding="utf-8")
    for a, b in replacements or []:
        text = text.replace(a, b)
    # drop first H1; the page chrome already has a title
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        text = "\n".join(lines[1:]).lstrip()
    return convert(text)


HOME_MAIN = """
  <div class="layout">
    <div>
      <p class="lede">Discussions, decisions, and status for the public website rebuild. The history site itself is Preview / Real / burrasa.net.</p>
      <div class="feed">
        <article class="card">
          <p class="when">2 September 2026</p>
          <h2><a href="news/2026-09-02-this-site/index.html">This working site</a></h2>
          <p>A House of Ur site for how we work on the rebuild: news and status in the main column, meetings listed beside it, process and glossary in the nav.</p>
        </article>
        <article class="card">
          <p class="when">29 August 2026</p>
          <h2><a href="news/2026-08-29-cutover/index.html">Cutover target: end of 2026</a></h2>
          <p>Preview with Barbara and Bob went well. Aim to point <code>burrasa.net</code> at House of Ur Real by the end of the year — parity, not perfection.</p>
        </article>
        <article class="card">
          <p class="when">28 August 2026 · meeting</p>
          <h2><a href="meetings/2026-08-28/index.html">Preview walkthrough</a></h2>
          <p>73 minutes on Preview. Contact, About, and a real home page are cutover must-haves. Maps and the Resources dump can follow.</p>
        </article>
      </div>
    </div>
    <aside class="rail">
      <h2>Meetings</h2>
      <ol>
        <li>
          <span class="when">28 Aug 2026</span>
          <a href="meetings/2026-08-28/index.html">Preview walkthrough</a>
          — Barbara Piscitelli, Bob Perry
        </li>
      </ol>
      <h2>Process</h2>
      <ul>
        <li><a href="process/index.html">How this workshop runs</a></li>
        <li><a href="process/transcription/index.html">How we transcribe meetings</a></li>
        <li><a href="glossary/index.html">Glossary</a></li>
      </ul>
    </aside>
  </div>
"""

NEWS_INDEX = """
  <div class="layout layout--single">
    <main class="paper prose">
      <h1>News</h1>
      <p class="lede">Status and significant work on the public site rebuild, newest first. Meetings also appear here when they change the plan.</p>
      <ul>
        <li><a href="../news/2026-09-02-this-site/index.html">2 Sep 2026 — This working site</a></li>
        <li><a href="../news/2026-08-29-cutover/index.html">29 Aug 2026 — Cutover target end of 2026</a></li>
        <li><a href="../meetings/2026-08-28/index.html">28 Aug 2026 — Preview walkthrough</a></li>
      </ul>
    </main>
  </div>
"""

NEWS_THIS_SITE = """
  <div class="layout layout--single">
    <article class="paper prose">
      <p class="when">2 September 2026 · news</p>
      <h1>This working site</h1>
      <p>The public history site is one thing. How we rebuild it is another. This House of Ur site is the second: a place for the History Group (and Johnny) to see discussions, decisions, meeting notes, and occasional status.</p>
      <p>Format is a small news list with a meetings list next to it on the home page. Significant work (a townships-map cleanup, a contact form that actually sends mail) can land as a news item. Meetings keep their own pages, including transcripts when we have them.</p>
      <p>It is <strong>not</strong> the public archive. Cream paper, but a workshop stamp. Links to Preview, Real, and the live cPanel site stay in the header.</p>
      <h2>What lives here</h2>
      <ul>
        <li>News / status</li>
        <li>Meetings (notes + transcript)</li>
        <li>Process (including how we transcribe recordings)</li>
        <li>Glossary of names and site jargon</li>
      </ul>
      <p>Raw stills, video, and timestamp JSON stay in the transcription workshop on disk — too bulky, and not what you need in a browser.</p>
    </article>
  </div>
"""

NEWS_CUTOVER = """
  <div class="layout layout--single">
    <article class="paper prose">
      <p class="when">29 August 2026 · status</p>
      <h1>Cutover target: end of 2026</h1>
      <p>After the 28 August Preview walkthrough, the working decision is: try to point <code>burrasa.net</code> at the House of Ur <strong>Real</strong> site by the end of 2026, so 2027 starts on the new site.</p>
      <p>Nobody is waiting for a perfect Resources dump. The bar is <strong>parity</strong> — don’t go backwards from what is already on the live cPanel site — plus a few things that must be right because they are about the organisation:</p>
      <ul>
        <li>A home page that isn’t only nav rectangles</li>
        <li>A contact form that actually works</li>
        <li>About / Inc. / meetings / Jenny Loftus leftovers cleaned up</li>
      </ul>
      <p>Maps and the long Resources lists can keep their existing problems across the cut. Details: <a href="../../meetings/2026-08-28/index.html">28 August meeting notes</a>.</p>
    </article>
  </div>
"""

MEETINGS_INDEX = """
  <div class="layout layout--single">
    <main class="paper prose">
      <h1>Meetings</h1>
      <p class="lede">Working sessions on the public site rebuild. Notes are the account we act on; transcripts are the tape.</p>
      <ul>
        <li>
          <a href="../meetings/2026-08-28/index.html">28 August 2026 — Preview walkthrough</a>
          — Emlyn O’Regan, Barbara Piscitelli, Bob Perry
          · <a href="../meetings/2026-08-28/transcript.html">transcript</a>
        </li>
      </ul>
    </main>
  </div>
"""

PROCESS_INDEX = """
  <div class="layout layout--single">
    <main class="paper prose">
      <h1>Process</h1>
      <p>How the rebuild is run. The public site repo is <code>bhgsite2026</code> (git branch <code>working</code> → Preview → approved → Real). This site is the workshop log. They are easy to confuse by name; they are not the same thing.</p>
      <h2>Two sites, one House</h2>
      <table>
        <thead><tr><th>Site</th><th>What it is</th></tr></thead>
        <tbody>
          <tr><td>Public history site</td><td>Preview <code>preview1845-bhg.house-of-ur.com</code>, Real <code>real-bhg.house-of-ur.com</code>. Content from <code>bhgsite2026</code>.</td></tr>
          <tr><td>BHG Site Working (this)</td><td>News, meetings, process. Content from <code>bhgsite-working</code>. Proposed URL <code>working-bhg.house-of-ur.com</code>.</td></tr>
        </tbody>
      </table>
      <h2>Fridays</h2>
      <p>The 28 August meeting asked to keep coming in on Fridays, fix one page at a time on Preview, rather than writing giant comment lists. Emlyn still needs to show the change method and give permission to edit Preview.</p>
      <h2>Documents</h2>
      <ul>
        <li><a href="../process/transcription/index.html">How we transcribe meetings</a></li>
        <li><a href="../glossary/index.html">Glossary</a></li>
        <li><a href="https://github.com/emlynoregan/bhgsite2026/blob/working/JOHNNY.md">Johnny’s public-site playbook</a> (on GitHub)</li>
      </ul>
    </main>
  </div>
"""

MEETING_FOOT = """
<p>Full tape: <a href="transcript.html">transcript</a>. Spellings: <a href="../../glossary/index.html">glossary</a>. How we made the notes: <a href="../../process/transcription/index.html">transcription method</a>.</p>
"""


def main() -> None:
    write("index.html", page(title="News", root="", main=HOME_MAIN, extra_class="home"))
    write("news/index.html", page(title="News index", root="../", main=NEWS_INDEX))
    write(
        "news/2026-09-02-this-site/index.html",
        page(title="This working site", root="../../", main=NEWS_THIS_SITE),
    )
    write(
        "news/2026-08-29-cutover/index.html",
        page(title="Cutover target end of 2026", root="../../", main=NEWS_CUTOVER),
    )
    write("meetings/index.html", page(title="Meetings", root="../", main=MEETINGS_INDEX))
    write("process/index.html", page(title="Process", root="../", main=PROCESS_INDEX))

    notes_md = DOCS / "meetings/2026-08-28/meeting-notes.md"
    notes_html = md(
        notes_md,
        replacements=[
            (
                "`gpt-4o-transcribe-diarize` is not on OpenRouter. Native OpenAI keys were not on this machine; House of Ur `secrets_dev.json` has the OpenRouter key used here.\n\n---\n\n",
                "",
            ),
            ("[transcript](transcript.md)", "[transcript](transcript.html)"),
            ("[transcription-methodology.md](../transcription-methodology.md)", "[transcription method](../../process/transcription/index.html)"),
            ("[stills-catalog.md](stills-catalog.md)", "the stills catalog (kept in the transcription workshop, not on this site)"),
            ("[glossary.md](../../glossary.md)", "[glossary](../../glossary/index.html)"),
        ],
    )
    # drop the local-files table; replace with site links
    cut = notes_html.find("<h2>Files in this folder</h2>")
    if cut != -1:
        notes_html = notes_html[:cut]
    notes_html += MEETING_FOOT
    write(
        "meetings/2026-08-28/index.html",
        page(
            title="Preview walkthrough — 28 August 2026",
            root="../../",
            main=f'<div class="layout layout--single"><article class="paper prose">{notes_html}</article></div>',
        ),
    )

    tr_html = md(
        DOCS / "meetings/2026-08-28/transcript.md",
        replacements=[
            ("[stills-catalog.md](stills-catalog.md)", "the stills catalog (workshop disk, not on this site)"),
            ("[meeting-notes.md](meeting-notes.md)", "[meeting notes](index.html)"),
            ("[glossary.md](../../glossary.md)", "[glossary](../../glossary/index.html)"),
        ],
    )
    write(
        "meetings/2026-08-28/transcript.html",
        page(
            title="Transcript — 28 August 2026",
            root="../../",
            extra_class="transcript-page",
            main=f'<div class="layout layout--single"><article class="paper prose transcript">{tr_html}</article></div>',
        ),
    )

    method = md(
        DOCS / "meetings/transcription-methodology.md",
        replacements=[
            ("[`../glossary.md`](../glossary.md)", "[glossary](../../glossary/index.html)"),
            ("[28 August 2026](2026-08-28/meeting-notes.md)", "[28 August 2026](../../meetings/2026-08-28/index.html)"),
            ("[2026-08-28/](2026-08-28/)", "[2026-08-28](../../meetings/2026-08-28/index.html)"),
            ("[`extract_stills.py`](extract_stills.py)", "<code>extract_stills.py</code>"),
            ("OpenRouter key: House of Ur `city-of-ur/deploy/secrets_dev.json` → `openrouter_api_key`. **Never print it. Never commit it.**", "OpenRouter key from House of Ur deploy secrets. **Never print it. Never commit it.**"),
            ("[README.md](README.md)", "the meetings index"),
            ("[`../language-ngadjuri.md`](../language-ngadjuri.md)", "the Ngadjuri language note in planning docs"),
        ],
    )
    write(
        "process/transcription/index.html",
        page(
            title="How we transcribe meetings",
            root="../../",
            main=f'<div class="layout layout--single"><article class="paper prose">{method}</article></div>',
        ),
    )

    gloss = md(
        DOCS / "glossary.md",
        replacements=[
            ("[language-ngadjuri.md](language-ngadjuri.md)", "Ngadjuri language note (planning docs)"),
            ("[meetings/transcription-methodology.md](meetings/transcription-methodology.md)", "[how we transcribe](../process/transcription/index.html)"),
        ],
    )
    # prepend this-site row into hosts table after convert is messy; add a note instead
    extra = """<p><strong>BHG Site Working</strong> (this site) is the rebuild workshop. House Site slug <code>working</code> → <a href="https://working-bhg.house-of-ur.com/">working-bhg.house-of-ur.com</a>. It is not the git branch <code>working</code> on the public site repo.</p>"""
    write(
        "glossary/index.html",
        page(
            title="Glossary",
            root="../",
            main=f'<div class="layout layout--single"><article class="paper prose">{extra}{gloss}</article></div>',
        ),
    )

    write(
        "404.html",
        page(
            title="Not found",
            root="./",
            main="""
  <div class="layout layout--single">
    <main class="paper prose">
      <h1>Not found</h1>
      <p>That path is not on this workshop site.</p>
      <p><a href="./index.html">Back to news</a></p>
    </main>
  </div>
""",
        ),
    )


if __name__ == "__main__":
    main()
