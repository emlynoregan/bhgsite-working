# Instructions for Johnny Green — BHG Site Working

**Who this is for:** Johnny Green (Dubsar in the Burra History Group House).  
**Repo:** `bhgsite-working` — workshop / news site for the **public** rebuild.  
**Not this repo:** [`bhgsite2026`](https://github.com/emlynoregan/bhgsite2026) (Preview + Real history site). That playbook is `bhgsite2026/JOHNNY.md`.

Spelling: *Johnny* (with a **y**).

---

## Your job

Keep this workshop site current: news items, meeting notes, process pages, and the published todo list. Git is the source of truth. Tickets are authored in `docs/projects/bhg-site/tickets/` and copied onto this site by `scripts/build.py`. On the site the list is labelled **Todo** (not Board). House of Ur Sites publishes a Library folder.

You do **not** create the House Site yourself. Ask Bel if the Site or Library folder is missing.

---

## Target Site

House: **Burra History Group** · slug **`bhg`** · id `9075a3ed-54e7-4162-8db8-54087cedac59`

| Role | Site slug | Site id | Library path | Public URL |
|------|-----------|---------|--------------|------------|
| This workshop (one Site) | `working` | `c856f601-e83f-4ae5-b3d8-7b8c7e399c8e` | `/sites/bhgsite-working/` | https://working-bhg.house-of-ur.com/ |

One Site is enough. Do **not** invent a Preview/Real pair for this workshop unless Bel asks.

Serving mode: **`github_pages`**. Authored links still use explicit `index.html`.

Local Bel publish (this machine): `python scripts/publish_hou_site.py --build` using `scripts/.env` (gitignored). Do not copy that key into this playbook.

---

## What to edit

| Kind | Where |
|------|--------|
| Home news cards, new posts, meetings index | `scripts/build.py` (then run it) |
| CSS | `source/css/working.css` |
| Meeting notes / transcript / glossary / transcription method / **tickets** | Prefer updating the markdown in `docs/projects/bhg-site/` on Bel’s machine, then `python scripts/build.py`. Todo HTML is generated from `tickets/` (URL `/board/`; label **Todo**). |
| This playbook | `JOHNNY.md` |

Never commit secrets, video, or stills.

---

## Build

```bash
python scripts/build.py
```

There is no Pagefind / npm step. `source/` is what you deploy.

---

## Deploy

1. Clean tree, current `main` (or whatever branch Bel names).  
2. `python scripts/build.py`  
3. Mirror **contents of `source/`** into `/sites/bhgsite-working/`:

   ```bash
   python /opt/scripts/library_push_folder.py \
     "$(pwd)/source" \
     "/sites/bhgsite-working/" \
     mirror
   ```

4. Refresh cache on the `working` Site.  
5. Smoke-check https://working-bhg.house-of-ur.com/index.html and one meeting page.

Do not deploy this repo to Preview or Real of the **public** history site.

---

## Bel setup (done 2026-09-02)

- [x] House Site slug **`working`**, Library `/sites/bhgsite-working/`, mode `github_pages`
- [x] Public hostname https://working-bhg.house-of-ur.com/
- [x] Site id `c856f601-e83f-4ae5-b3d8-7b8c7e399c8e`
- [ ] Attach git access when this repo has a GitHub remote
