"""Parse BHG tickets in docs and emit board + ticket HTML."""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

DOCS = Path(r"C:\Users\emlyn\Documents\emlyn\docs\projects\bhg-site")
TICKETS_DIR = DOCS / "tickets"

COLUMNS = ("Now", "Next", "Cutover", "Later", "Done")

META_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")
TITLE_RE = re.compile(r"^# (BHG-\d+):\s*(.+)$")
SLUG_RE = re.compile(r"^(BHG-(\d+)-[a-z0-9-]+)\.md$")

DOC_HREFS = {
    "../meetings/2026-09-04/meeting-notes.md": "meetings/2026-09-04/index.html",
    "../meetings/2026-09-04/transcript.md": "meetings/2026-09-04/transcript.html",
    "../meetings/2026-08-28/meeting-notes.md": "meetings/2026-08-28/index.html",
    "../meetings/2026-08-28/transcript.md": "meetings/2026-08-28/transcript.html",
    "../useful-links.md": "process/useful-links/index.html",
    "../glossary.md": "glossary/index.html",
}


@dataclass
class Ticket:
    path: Path
    slug: str
    number: int
    id: str
    title: str
    status: str
    column: str
    who: str
    where: str
    size: str
    depends: str
    check: str
    goal: str
    body_md: str


def _meta(lines: list[str]) -> tuple[dict[str, str], int]:
    meta: dict[str, str] = {}
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        m = META_RE.match(line)
        if not m:
            break
        meta[m.group(1).strip().lower()] = m.group(2).strip()
        i += 1
    return meta, i


def _goal(text: str) -> str:
    parts = re.split(r"^## ", text, flags=re.M)
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        if heading.strip() != "Goal":
            continue
        for para in body.strip().split("\n\n"):
            para = para.strip()
            if para and not para.startswith("#"):
                return " ".join(para.split())
    return ""


def parse_ticket(path: Path) -> Ticket:
    slug_m = SLUG_RE.match(path.name)
    if not slug_m:
        raise ValueError(f"Unexpected ticket filename: {path.name}")
    slug = slug_m.group(1)
    number = int(slug_m.group(2))
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title_m = TITLE_RE.match(lines[0] if lines else "")
    if not title_m:
        raise ValueError(f"Ticket {path.name} needs an H1 like '# BHG-001: Title'")
    ident, title = title_m.group(1), title_m.group(2).strip()
    meta, body_start = _meta(lines)
    body = "\n".join(lines[body_start:]).lstrip()
    column = meta.get("column", "Later")
    if column not in COLUMNS:
        column = "Later"
    return Ticket(
        path=path,
        slug=slug,
        number=number,
        id=ident,
        title=title,
        status=meta.get("status", "Proposed"),
        column=column,
        who=meta.get("who", "—"),
        where=meta.get("where", "—"),
        size=meta.get("size", "—"),
        depends=meta.get("depends on", "—"),
        check=meta.get("check", ""),
        goal=_goal(text),
        body_md=body,
    )


def load_tickets(folder: Path | None = None) -> list[Ticket]:
    folder = folder or TICKETS_DIR
    out: list[Ticket] = []
    for path in sorted(folder.glob("BHG-*.md")):
        if path.name.startswith("BHG-000"):
            continue
        out.append(parse_ticket(path))
    return sorted(out, key=lambda t: t.number)


def rewrite_ticket_md(text: str, *, depth: int) -> str:
    prefix = "../" * depth
    for src, dest in DOC_HREFS.items():
        text = text.replace(f"]({src})", f"]({prefix}{dest})")
    if depth == 1:
        text = re.sub(r"\]\((BHG-\d+-[a-z0-9-]+)\.md\)", r"](\1/index.html)", text)
        text = text.replace("](README.md)", "](index.html)")
        text = text.replace("](BHG-000-template.md)", "](index.html)")
    else:
        text = re.sub(
            r"\]\((BHG-\d+-[a-z0-9-]+)\.md\)",
            r"](../\1/index.html)",
            text,
        )
        text = text.replace("](README.md)", "](../index.html)")
        text = text.replace("](BHG-000-template.md)", "](../index.html)")
    return text


def _plain(text: str) -> str:
    text = text.replace("`", "")
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    return html.escape(text)


def _pill(status: str) -> str:
    slug = re.sub(r"[^a-z]+", "-", status.lower()).strip("-")
    return f'<span class="pill pill--{html.escape(slug)}">{html.escape(status)}</span>'


def _check_href(text: str) -> str | None:
    text = (text or "").strip()
    if text.startswith("http://") or text.startswith("https://"):
        return text
    m = re.match(r"^\[([^\]]+)\]\((https?://[^)]+)\)$", text)
    if m:
        return m.group(2)
    return None


def _check_html(text: str, *, label: str = "Check on Preview") -> str:
    href = _check_href(text)
    if not href:
        return html.escape(text)
    return f'<a href="{html.escape(href)}">{html.escape(label)}</a>'


def board_main(tickets: list[Ticket]) -> str:
    cols: list[str] = []
    by_col: dict[str, list[Ticket]] = {c: [] for c in COLUMNS}
    for t in tickets:
        by_col.setdefault(t.column, []).append(t)
    for name in COLUMNS:
        cards = []
        for t in by_col.get(name, []):
            goal = _plain(t.goal) if t.goal else ""
            check = (
                f'<p class="ticket-card__check">{_check_html(t.check)}</p>'
                if _check_href(t.check)
                else ""
            )
            cards.append(
                f"""
        <article class="ticket-card">
          <p class="ticket-card__id">{html.escape(t.id)} · {_pill(t.status)}</p>
          <h3><a href="{html.escape(t.slug)}/index.html">{html.escape(t.title)}</a></h3>
          <p class="ticket-card__who">{html.escape(t.who)} · {html.escape(t.where)}</p>
          {"<p>" + goal + "</p>" if goal else ""}
          {check}
        </article>"""
            )
        body = "".join(cards) or '<p class="ticket-card__empty">None</p>'
        cols.append(
            f"""
      <section class="kanban__col" aria-labelledby="col-{name.lower()}">
        <h2 id="col-{name.lower()}">{html.escape(name)} <span>{len(by_col.get(name, []))}</span></h2>
        {body}
      </section>"""
        )
    kanban = "\n".join(cols)
    return f"""
  <div class="layout layout--single">
    <div class="paper prose">
      <h1>Todo</h1>
      <p class="lede">Open work for the public history-site rebuild. Markdown in the planning docs is the source of truth; this page is the published copy. One item is one cohesive change.</p>
      <p>Work one <strong>Ready</strong> ticket at a time from <strong>Now</strong>. Cutover is end of 2026 — parity with <code>burrasa.net</code>, plus a working contact form and a real home page. Do not deploy Preview work to Real unless the group has asked.</p>
    </div>
    <div class="kanban" role="list">
      {kanban}
    </div>
  </div>
"""


def ticket_main(ticket: Ticket, body_html: str) -> str:
    rows = [
        ("Status", html.escape(ticket.status)),
        ("Column", html.escape(ticket.column)),
        ("Who", html.escape(ticket.who)),
        ("Where", html.escape(ticket.where)),
        ("Size", html.escape(ticket.size)),
        ("Depends on", html.escape(ticket.depends)),
    ]
    if _check_href(ticket.check):
        rows.append(("Check", _check_html(ticket.check)))
    dl = "".join(f"<div><dt>{html.escape(k)}</dt><dd>{v}</dd></div>" for k, v in rows)
    return f"""
  <div class="layout layout--single">
    <article class="paper prose ticket">
      <p class="when"><a href="../index.html">Todo</a> · {html.escape(ticket.id)}</p>
      <h1>{html.escape(ticket.title)}</h1>
      <dl class="ticket-meta">{dl}</dl>
      {body_html}
    </article>
  </div>
"""


def now_tickets(tickets: list[Ticket]) -> list[Ticket]:
    return [t for t in tickets if t.column == "Now"]
