# BHG Site Working

Workshop site for the Burra History Group **public website rebuild**. News and status in the main column; meetings listed beside them. Not the public history site.

| | |
|--|--|
| **House** | Burra History Group (`bhg`) |
| **Site slug** | `working` |
| **URL** | https://working-bhg.house-of-ur.com/ |
| **Library path** | `/sites/bhgsite-working/` |
| **Site id** | `c856f601-e83f-4ae5-b3d8-7b8c7e399c8e` |
| **Repo** | this folder (`bhgsite-working`) |
| **Public history site** | [`bhgsite2026`](../bhgsite2026/) → Preview / Real |

Browse `source/` locally, or the live Site. Ops: [JOHNNY.md](JOHNNY.md).

## Format

- **News** — status and significant work, newest first. Meetings that change the plan also get a news card.
- **Meetings rail** — compact dated list on the home page; full notes + transcript under `/meetings/`.
- **Todo** — published copy of tickets in `docs/projects/bhg-site/tickets/` (that folder is the source of truth). Label on the site is Todo, not Board; the URL stays `/board/`.
- **Process / glossary** — how we transcribe, names and IA.

Do not put video, wav chunks, API keys, or JPEG stills here. Those stay in the transcription workshop (`docs/projects/bhg-site/meetings/`).

## Build

```bash
python scripts/build.py
```

That refreshes HTML generated from the docs markdown (meeting notes, transcript, methodology, glossary, **tickets**). Hand-authored pages (home, news posts, process index) live in `scripts/build.py` too. Chrome is `scripts/chrome.py`. Tickets: `scripts/tickets.py`.

Edit `source/css/working.css` directly.

Local preview:

```bash
python -m http.server 8765 --directory source
```

Then http://localhost:8765/index.html

## Deploy

`python scripts/publish_hou_site.py --build` (Bel machine; `scripts/.env` gitignored) or Johnny’s Library mirror. Then refresh cache. One Site is enough — this is not Preview/Real for the public archive.
