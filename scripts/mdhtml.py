"""Minimal markdown → HTML for BHG Site Working pages (stdlib only)."""
from __future__ import annotations

import html
import re


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<img src="\2" alt="\1">',
        text,
    )
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(
        r"\[\^([^\]]+)\]",
        r'<sup class="fnref" id="fnref-\1"><a href="#fn-\1">\1</a></sup>',
        text,
    )
    return text


def convert(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    in_ul = False
    in_code = False
    code_lines: list[str] = []

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                close_ul()
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if re.match(r"^\|.+\|$", line) and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            close_ul()
            headers = [c.strip() for c in line.strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and re.match(r"^\|.+\|$", lines[i]):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            out.append("<table>")
            out.append("<thead><tr>" + "".join(f"<th>{inline(h)}</th>" for h in headers) + "</tr></thead>")
            out.append("<tbody>")
            for row in rows:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            out.append("</tbody></table>")
            continue

        if line.strip() == "---":
            close_ul()
            out.append("<hr>")
            i += 1
            continue

        fn = re.match(r"^\[\^([^\]]+)\]:\s+(.*)$", line)
        if fn:
            close_ul()
            out.append(
                f'<p class="fn" id="fn-{html.escape(fn.group(1))}">'
                f'<a href="#fnref-{html.escape(fn.group(1))}">^{html.escape(fn.group(1))}</a> '
                f"{inline(fn.group(2))}</p>"
            )
            i += 1
            continue

        m = re.match(r"^(#{1,4}) (.+)$", line)
        if m:
            close_ul()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        img = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
        if img:
            close_ul()
            alt = html.escape(img.group(1))
            src = html.escape(img.group(2), quote=True)
            out.append(f'<figure><img src="{src}" alt="{alt}"></figure>')
            i += 1
            continue

        check = re.match(r"^- \[([ xX])\] (.*)$", line)
        if check:
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            checked = ' checked' if check.group(1).lower() == "x" else ""
            out.append(
                f'<li class="check"><input type="checkbox" disabled{checked}> {inline(check.group(2))}</li>'
            )
            i += 1
            continue

        if re.match(r"^- ", line):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(line[2:])}</li>")
            i += 1
            continue

        if re.match(r"^\d+\. ", line):
            close_ul()
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            out.append("<ol>")
            for item in items:
                out.append(f"<li>{inline(item)}</li>")
            out.append("</ol>")
            continue

        if not line.strip():
            close_ul()
            i += 1
            continue

        close_ul()
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") and not lines[i].startswith("- ") and not lines[i].startswith("```") and not re.match(r"^\d+\. ", lines[i]) and lines[i].strip() != "---" and not re.match(r"^\|", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + "<br>\n".join(inline(p) for p in para) + "</p>")

    close_ul()
    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    return "\n".join(out)
