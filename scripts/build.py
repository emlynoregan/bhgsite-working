"""Build BHG Site Working HTML under source/."""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chrome import page, write  # noqa: E402
from mdhtml import convert  # noqa: E402
from tickets import board_main, load_tickets, now_tickets, rewrite_ticket_md, ticket_main  # noqa: E402

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
      <p class="lede">Discussions, decisions, and status for the public website rebuild. The history site itself is Preview / Real / burrasa.net. Open work is on the <a href="board/index.html">todo list</a>.</p>
      <div class="feed">
        <article class="card">
          <p class="when">11 September 2026</p>
          <h2><a href="process/bibliography/index.html">Harvard citations from the NLA</a></h2>
          <p>Working list for titles already on the site. <em>School Daze</em> corrected on Preview. Publisher clashes (Monster Mine, and a few others) wait for Barbara.</p>
        </article>
        <article class="card">
          <p class="when">11 September 2026</p>
          <h2><a href="board/index.html">Todo</a></h2>
          <p>The 4 September actions (and the leftover 28 August cutover items) are on the todo list. Planning docs stay the source of truth; this site publishes the copy.</p>
        </article>
        <article class="card">
          <p class="when">4 September 2026 · meeting</p>
          <h2><a href="meetings/2026-09-04/index.html">Publications, Useful Links, Jodie’s list</a></h2>
          <p>Four Pixel clips and phone stills. Publications bibliography and a Publications nav; they reviewed the Useful Links inventory; contact form; names for Jodie; Publisher is in hand.</p>
        </article>
        <article class="card">
          <p class="when">4 September 2026</p>
          <h2><a href="process/useful-links/index.html">Useful Links inventory</a></h2>
          <p>Every external href on Resources, checked today. Working replacements, alternatives, and Wayback for the ones that don’t. familyhistorysa.org is a casino — those six hrefs should come off Preview first.</p>
        </article>
        <article class="card">
          <p class="when">4 September 2026</p>
          <h2><a href="news/2026-09-04-preview-copy/index.html">Copy pass on Preview</a></h2>
          <p>Contacts, About, Help, Heritage, shop leftovers, captions, Resources labels, and new-tab externals are live on Preview. Contact form and home page still outstanding.</p>
        </article>
        <article class="card">
          <p class="when">4 September 2026</p>
          <h2><a href="news/2026-09-04-august-leftovers/index.html">What’s left from 28 August</a></h2>
          <p>Surname-query duplicates and the copy list are on Preview. What remains needs the group, a design pass, or a form that actually sends mail.</p>
        </article>
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
      <h2>Todo</h2>
      <p class="when">Now</p>
      <ol>
        __NOW_TICKETS__
      </ol>
      <p><a href="board/index.html">Full list</a></p>
      <h2>Meetings</h2>
      <ol>
        <li>
          <span class="when">4 Sep 2026</span>
          <a href="meetings/2026-09-04/index.html">Publications, Useful Links, Jodie’s list</a>
          — Barbara Piscitelli, Bob Perry
        </li>
        <li>
          <span class="when">28 Aug 2026</span>
          <a href="meetings/2026-08-28/index.html">Preview walkthrough</a>
          — Barbara Piscitelli, Bob Perry
        </li>
      </ol>
      <h2>Process</h2>
      <ul>
        <li><a href="process/index.html">How this workshop runs</a></li>
        <li><a href="board/index.html">Todo</a></li>
        <li><a href="process/useful-links/index.html">Useful Links inventory</a></li>
        <li><a href="process/bibliography/index.html">Harvard citations (NLA)</a></li>
        <li><a href="process/transcription/index.html">How we transcribe meetings</a></li>
        <li><a href="glossary/index.html">Glossary</a></li>
      </ul>
      <h2>Prototypes</h2>
      <ul>
        <li><a href="https://emlynoregan.com/bitn/" target="_blank" rel="noopener">Burra in the News</a></li>
        <li><a href="https://bda-dev.emlynoregan.com/" target="_blank" rel="noopener">Burra Digital Archive</a></li>
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
        <li><a href="../board/index.html">11 Sep 2026 — Todo</a></li>
        <li><a href="../process/bibliography/index.html">11 Sep 2026 — Harvard citations (NLA draft)</a></li>
        <li><a href="../meetings/2026-09-04/index.html">4 Sep 2026 — Publications, Useful Links, Jodie’s list</a></li>
        <li><a href="../process/useful-links/index.html">4 Sep 2026 — Useful Links inventory (replacements + Wayback)</a></li>
        <li><a href="../news/2026-09-04-preview-copy/index.html">4 Sep 2026 — Copy pass on Preview</a></li>
        <li><a href="../news/2026-09-04-august-leftovers/index.html">4 Sep 2026 — What’s left from 28 August</a></li>
        <li><a href="../news/2026-09-02-this-site/index.html">2 Sep 2026 — This working site</a></li>
        <li><a href="../news/2026-08-29-cutover/index.html">29 Aug 2026 — Cutover target end of 2026</a></li>
        <li><a href="../meetings/2026-08-28/index.html">28 Aug 2026 — Preview walkthrough</a></li>
      </ul>
    </main>
  </div>
"""

NEWS_PREVIEW_COPY = """
  <div class="layout layout--single">
    <article class="paper prose">
      <p class="when">4 September 2026 · status</p>
      <h1>Copy pass on Preview</h1>
      <p>The organisational copy from the <a href="../../meetings/2026-08-28/index.html">28 August walkthrough</a> is now on <a href="https://preview1845-bhg.house-of-ur.com/">Preview</a>. Real was not touched.</p>
      <ul>
        <li>Research contacts — Doidge gone; Burra Community Library; no second Thursday; website and join queries go to Contact.</li>
        <li>Research guidelines — fake “Burra Family History Group” mailtos replaced with Contact.</li>
        <li>About the group — Inc. dropped from the heading; plaques 46 → 84; Facebook is a normal sentence, and on Contact as well.</li>
        <li>Help — scanner / PCMag block gone; no fake upload button.</li>
        <li>Heritage — capital-I Indigenous.</li>
        <li>Shop leftovers — no “download files,” data-CD pitch, or VIC priced list. The 2017 booklet table stays as a list, not a shop.</li>
        <li>Captions — Burra Cemetery Register; school and marriages credits say Burra Community Library.</li>
        <li>Resources hub tile is <strong>Genealogical research</strong>, matching the page title.</li>
        <li>Off-site links open in a new tab.</li>
      </ul>
      <p>Surname-query duplicates were already collapsed. What is still open is on <a href="../2026-09-04-august-leftovers/index.html">What’s left from 28 August</a> — contact form, home page, maps, and the rest that needs more than a text edit.</p>
    </article>
  </div>
"""

NEWS_AUGUST_LEFTOVERS = """
  <div class="layout layout--single">
    <article class="paper prose">
      <p class="when">4 September 2026 · status</p>
      <h1>What’s left from 28 August</h1>
      <p>A pass through the <a href="../../meetings/2026-08-28/index.html">28 August Preview walkthrough</a> against Preview. Surname duplicates and the copy list are done (see <a href="../2026-09-04-preview-copy/index.html">Copy pass on Preview</a>). What is left still needs the group, a design pass, or a form that actually sends mail.</p>
      <h2>Done</h2>
      <p>Consecutive duplicate surname queries on the research page are collapsed. Preview now has 300 unique essays instead of the same compiled note repeated under neighbouring headings (Cherry/Kidd, Hinch/Torrens/McBurnie, and the rest of that run). Old anchors still work. Live on <a href="https://preview1845-bhg.house-of-ur.com/resources/research/index.html">Preview</a>.</p>
      <p>Copy pass, 4 September:</p>
      <ul>
        <li><strong>Research contacts</strong> — Elizabeth Doidge dropped as website-designer contact; Burra Community Library, not “Burra Library”; no “meets on the second Thursday.”</li>
        <li><strong>Fake “Burra Family History Group”</strong> mailtos on the research guidelines replaced with Contact.</li>
        <li><strong>About the group</strong> — Inc. dropped from the heading; plaques 46 → 84; March 2016 Facebook heading replaced; Facebook on Contact as well.</li>
        <li><strong>Help</strong> — scanner / PCMag block deleted; no promised upload button on Contact.</li>
        <li><strong>Heritage</strong> — capital-I Indigenous in the listing quote.</li>
        <li><strong>Shop leftovers</strong> — “Download files available for purchase,” data-CD copy, and VIC books-for-sale list stripped.</li>
        <li><strong>Captions</strong> — “Burra Cemetery Register”; school registers “from Burra Community Library.”</li>
        <li><strong>Resources nav</strong> — tile is Genealogical research, matching the page title.</li>
        <li><strong>External links</strong> — open in a new tab.</li>
      </ul>
      <h2>Needs more than a text edit</h2>
      <ul>
        <li><strong>Working contact form.</strong> The page is still a disabled stub. Cutover must-have; needs an inbox and a mail path, not more HTML.</li>
        <li><strong>Home page.</strong> Cutover must-have: not only nav rectangles — featured/new stories and some visual invention.</li>
        <li><strong>Maps / township cut-outs</strong> — Bob’s “where is this in Burra?” frame. Parked in the meeting.</li>
        <li><strong>Tindale provenance</strong> / book link Emlyn thought he’d already sent.</li>
        <li><strong>Dead useful-links.</strong> Inventory plus replacements: <a href="../../process/useful-links/index.html">Useful Links, 4 September</a>. familyhistorysa.org is a casino — pull those six hrefs first. The rest is retarget / Wayback / editorial with Barbara.</li>
        <li><strong>Surname browse + search.</strong> Duplicate <em>blocks</em> are gone; a real browse/search page is a new feature.</li>
        <li><strong>Publisher files / booklet PDFs.</strong> September machinery, plus Barbara and the treasurer before anything BHG-owned goes online.</li>
        <li><strong>Friday working-group: how to edit Preview</strong> — a session, not a code change.</li>
        <li><strong>People / methodology pages</strong> (Auhl, Fuss, Meredith, how the site was made) — writing, and the Lisa / Auhl-collection visit.</li>
        <li><strong>Barbara’s Google Doc</strong> rewrite of About/help. Bob asked not to rebuild About from scratch; we can patch the dead bits without replacing her rewrite.</li>
        <li><strong>Nature and Heritage Walk GPS overlay</strong> (Bob; not on the live site).</li>
        <li><strong>Goyder VIC + Town Hall licence</strong> — later, not a cutover blocker.</li>
      </ul>
      <p>Also not blocking cutover, same class of problem as <code>burrasa.net</code>: People hub gaps (Cornish/Welsh), leftover surname copies that were not sitting next to each other, duplicate wedding-table rows, Mongolata sourcing, a donate button.</p>
    </article>
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
        <li>Todo (open work, published from the planning docs)</li>
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
          <a href="../meetings/2026-09-04/index.html">4 September 2026 — Publications, Useful Links, Jodie’s list</a>
          — Emlyn O’Regan, Barbara Piscitelli, Bob Perry
          · <a href="../meetings/2026-09-04/transcript.html">transcript</a>
        </li>
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
          <tr><td>BHG Site Working (this)</td><td>News, meetings, process. Content from <code>bhgsite-working</code>. URL <code>working-bhg.house-of-ur.com</code>.</td></tr>
        </tbody>
      </table>
      <h2>Related prototypes</h2>
      <p>Separate from the public history site rebuild:</p>
      <ul>
        <li><a href="https://emlynoregan.com/bitn/" target="_blank" rel="noopener">Burra in the News</a> — Eric Fuss newspaper archive (1845–2016)</li>
        <li><a href="https://bda-dev.emlynoregan.com/" target="_blank" rel="noopener">Burra Digital Archive</a> — archive prototype</li>
      </ul>
      <h2>Fridays</h2>
      <p>The 28 August meeting asked to keep coming in on Fridays, fix one page at a time on Preview, rather than writing giant comment lists. Emlyn still needs to show the change method and give permission to edit Preview.</p>
      <h2>Todo</h2>
      <p>Open work lives in the BHG planning docs and is published on this site: <a href="../board/index.html">Todo</a>. One item is one cohesive change. Preview vs Real still follows the usual rule — do not ship to Real unless the group has asked.</p>
      <h2>Documents</h2>
      <ul>
        <li><a href="../board/index.html">Todo</a></li>
        <li><a href="../process/transcription/index.html">How we transcribe meetings</a></li>
        <li><a href="../process/useful-links/index.html">Useful Links inventory (replacements + Wayback)</a></li>
        <li><a href="../process/bibliography/index.html">Harvard citations (NLA draft)</a></li>
        <li><a href="../glossary/index.html">Glossary</a></li>
        <li><a href="https://github.com/emlynoregan/bhgsite2026/blob/working/JOHNNY.md">Johnny’s public-site playbook</a> (on GitHub)</li>
      </ul>
    </main>
  </div>
"""

MEETING_FOOT = """
<p>Full tape: <a href="transcript.html">transcript</a>. Spellings: <a href="../../glossary/index.html">glossary</a>. How we made the notes: <a href="../../process/transcription/index.html">transcription method</a>.</p>
"""


def write_board() -> list:
    tickets = load_tickets()
    write(
        "board/index.html",
        page(
            title="Todo",
            root="../",
            extra_class="board-page",
            main=board_main(tickets),
            description="Todo list for the Burra History Group public website rebuild.",
        ),
    )
    for ticket in tickets:
        body_html = convert(rewrite_ticket_md(ticket.body_md, depth=2))
        write(
            f"board/{ticket.slug}/index.html",
            page(
                title=f"{ticket.id}: {ticket.title}",
                root="../../",
                main=ticket_main(ticket, body_html),
            ),
        )
    return tickets


def home_main(tickets: list) -> str:
    items = []
    for ticket in now_tickets(tickets):
        items.append(
            "<li>"
            f'<a href="board/{html.escape(ticket.slug)}/index.html">{html.escape(ticket.id)}</a>'
            f" — {html.escape(ticket.title)}"
            "</li>"
        )
    now_html = "\n        ".join(items) or "<li>Nothing in Now.</li>"
    return HOME_MAIN.replace("__NOW_TICKETS__", now_html)


def main() -> None:
    tickets = write_board()
    write("index.html", page(title="News", root="", main=home_main(tickets), extra_class="home"))
    write("news/index.html", page(title="News index", root="../", main=NEWS_INDEX))
    write(
        "news/2026-09-04-preview-copy/index.html",
        page(title="Copy pass on Preview", root="../../", main=NEWS_PREVIEW_COPY),
    )
    write(
        "news/2026-09-04-august-leftovers/index.html",
        page(title="What’s left from 28 August", root="../../", main=NEWS_AUGUST_LEFTOVERS),
    )
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

    notes_html_sep = md(
        DOCS / "meetings/2026-09-04/meeting-notes.md",
        replacements=[
            ("[transcript](transcript.md)", "[transcript](transcript.html)"),
            ("[transcription-methodology.md](../transcription-methodology.md)", "[transcription method](../../process/transcription/index.html)"),
            ("[stills-catalog.md](stills-catalog.md)", "the stills catalog (kept in the transcription workshop, not on this site)"),
            ("[glossary.md](../../glossary.md)", "[glossary](../../glossary/index.html)"),
            ("[`tickets/`](../../tickets/README.md)", "[tickets](../../board/index.html)"),
        ],
    )
    cut_sep = notes_html_sep.find("<h2>Files in this folder</h2>")
    if cut_sep != -1:
        notes_html_sep = notes_html_sep[:cut_sep]
    notes_html_sep += MEETING_FOOT
    write(
        "meetings/2026-09-04/index.html",
        page(
            title="Publications, Useful Links, Jodie’s list — 4 September 2026",
            root="../../",
            main=f'<div class="layout layout--single"><article class="paper prose">{notes_html_sep}</article></div>',
        ),
    )

    tr_html_sep = md(
        DOCS / "meetings/2026-09-04/transcript.md",
        replacements=[
            ("[stills-catalog.md](stills-catalog.md)", "the stills catalog (workshop disk, not on this site)"),
            ("[meeting-notes.md](meeting-notes.md)", "[meeting notes](index.html)"),
            ("[glossary.md](../../glossary.md)", "[glossary](../../glossary/index.html)"),
        ],
    )
    write(
        "meetings/2026-09-04/transcript.html",
        page(
            title="Transcript — 4 September 2026",
            root="../../",
            extra_class="transcript-page",
            main=f'<div class="layout layout--single"><article class="paper prose transcript">{tr_html_sep}</article></div>',
        ),
    )

    method = md(
        DOCS / "meetings/transcription-methodology.md",
        replacements=[
            ("[`../glossary.md`](../glossary.md)", "[glossary](../../glossary/index.html)"),
            ("[28 August 2026](2026-08-28/meeting-notes.md)", "[28 August 2026](../../meetings/2026-08-28/index.html)"),
            ("[2026-08-28/](2026-08-28/)", "[2026-08-28](../../meetings/2026-08-28/index.html)"),
            ("[28 August 2026](2026-08-28/):", "[28 August 2026](../../meetings/2026-08-28/index.html):"),
            ("[4 September 2026](2026-09-04/):", "[4 September 2026](../../meetings/2026-09-04/index.html):"),
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

    links_html = md(
        DOCS / "useful-links.md",
        replacements=[
            ("[28 August walkthrough](meetings/2026-08-28/meeting-notes.md)", "[28 August walkthrough](../../meetings/2026-08-28/index.html)"),
            ("**On this workshop site:** published as a process page.\n\n", ""),
        ],
    )
    write(
        "process/useful-links/index.html",
        page(
            title="Useful Links inventory",
            root="../../",
            extra_class="inventory-page",
            main=f'<div class="layout layout--single"><article class="paper prose">{links_html}</article></div>',
        ),
    )

    bib_html = md(
        DOCS / "bibliography.md",
        replacements=[
            ("[tickets/BHG-005-harvard-citations.md](tickets/BHG-005-harvard-citations.md)", "[BHG-005](../../board/BHG-005-harvard-citations/index.html)"),
            ("[BHG-005](tickets/BHG-005-harvard-citations.md)", "[BHG-005](../../board/BHG-005-harvard-citations/index.html)"),
            ("[BHG-006](tickets/BHG-006-publications-nav.md)", "[BHG-006](../../board/BHG-006-publications-nav/index.html)"),
            ("[BHG-009](tickets/BHG-009-publisher-conversion.md)", "[BHG-009](../../board/BHG-009-publisher-conversion/index.html)"),
            ("[BHG-019](tickets/BHG-019-woolgangi-show-copyright.md)", "[BHG-019](../../board/BHG-019-woolgangi-show-copyright/index.html)"),
        ],
    )
    write(
        "process/bibliography/index.html",
        page(
            title="Harvard citations from the NLA",
            root="../../",
            extra_class="inventory-page",
            main=f'<div class="layout layout--single"><article class="paper prose">{bib_html}</article></div>',
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
