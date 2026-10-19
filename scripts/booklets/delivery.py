#!/usr/bin/env python3
"""BHG-028: gated, resumable House Library transfer for approved booklet assets.

The DEFAULT mode is offline and makes no House API calls or uploads (it can create a local unapproved decisions template). --execute requires
--confirm-publication plus independent, per-title/per-format editorial and
rights approval in an explicitly scoped local decision file. A successful
transfer to this Site Library IS PUBLIC, even without a website navigation link.

No automatic deletion, folder pruning, CDN invalidation or Site updates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from contextlib import contextmanager
import time
import urllib.error
import urllib.request
from pathlib import Path

from assets import WORKSPACE, PREFIX, digest, safe_file, validate

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from publish_hou_site import (
    DEFAULT_HOUSE_ID, DEFAULT_API_BASE, api_json, exchange_token, load_hou_config,
)

RELEASE_DIR = WORKSPACE / "booklet-release"
MANIFEST_PATH = RELEASE_DIR / "asset-manifest.json"
APPROVALS_PATH = RELEASE_DIR / "publication-decisions.json"
JOURNAL_PATH = RELEASE_DIR / "upload-journal.json"
SITE_BASE = "https://working-bhg.house-of-ur.com"
FORMAT_NAMES = {"reader", "pdf", "publisher"}
BUFFER_SIZE = 1024 * 1024


@contextmanager
def exclusive_transfer_lock(path: Path):
    """One writer per BHG release journal; survives agent restarts safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if path.stat().st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if sys.platform == "win32":
            import msvcrt
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("Another booklet upload is active; do not run concurrently") from exc
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError("Another booklet upload is active") from exc
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_suffix(".tmp")
    staging.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    staging.replace(path)


def decisions_template(manifest: dict) -> dict:
    return {
        "schema": 1, "destination": PREFIX, "manifest_sha256": manifest["manifest_sha256"],
        "publicly_accessible": True, "publication_authorised": False,
        "approval_reference": "", "decision_made_by": "", "approved_title_formats": {},
        "notes": "DRAFT. Public website file paths are accessible even without navigation links.",
    }


def ensure_decisions(manifest: dict, path: Path) -> dict:
    if not path.exists():
        atomic_json(path, decisions_template(manifest))
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("schema") != 1 or d.get("destination") != PREFIX:
        raise ValueError("Invalid publication decisions file destination or version")
    if d.get("manifest_sha256") != manifest["manifest_sha256"]:
        raise ValueError("Publication decisions are stale for a different manifest")
    return d


def authorise(decisions: dict, selected: list[dict], *, explicit: bool) -> None:
    if not explicit:
        raise PermissionError("Missing --confirm-publication; site files are publicly readable")
    if decisions.get("publication_authorised") is not True:
        raise PermissionError("Global BHG publication approval is not recorded")
    if not decisions.get("approval_reference", "").strip() or not decisions.get("decision_made_by", "").strip():
        raise PermissionError("Missing approval reference and responsible person")
    approved = decisions.get("approved_title_formats") or {}
    for asset in selected:
        record = approved.get(str(asset["catalog_number"]), {})
        if record.get(asset["kind"]) is not True:
            raise PermissionError(
                f"No editorial/rights approval for booklet {asset['catalog_number']:02d} / {asset['kind']}"
            )


def select(manifest: dict, titles: list[int], kinds: list[str]) -> list[dict]:
    if not titles or not kinds:
        raise ValueError("An explicit --titles selection and at least one --kinds format required")
    if any(kind not in FORMAT_NAMES for kind in kinds):
        raise ValueError("Invalid format name")
    valid_ids = {a["catalog_number"] for a in manifest["assets"]}
    if any(t not in valid_ids for t in titles):
        raise ValueError("Selected title is missing/unrecovered")
    wanted = {a["catalog_number"] for a in manifest["assets"] if a["kind"] in kinds}
    if any(t not in wanted for t in titles):
        raise ValueError("No assets for one selected title")
    return [a for a in manifest["assets"] if a["catalog_number"] in titles and a["kind"] in kinds]


def load_journal(path: Path, manifest: dict) -> dict:
    if not path.exists():
        return {"schema": 1, "destination": PREFIX, "verified": {}}
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != 1 or obj.get("destination") != PREFIX:
        raise ValueError("Unexpected journal schema or destination")
    if not isinstance(obj.get("verified"), dict):
        raise ValueError("Invalid transfer journal")
    return obj


def receipt_matches(asset: dict, journal: dict) -> bool:
    row = journal["verified"].get(asset["library_path"], {})
    return (row.get("sha256") == asset["sha256"] and row.get("size") == asset["size"]
            and row.get("public_bytes_verified") is True)


def stream_file(path: Path, block_size: int = BUFFER_SIZE):
    with path.open("rb") as f:
        while chunk := f.read(block_size):
            yield chunk


def upload_stream(url: str, asset: dict, path: Path, *, timeout_s: int = 1200) -> None:
    # API-provided presigned URLs are treated as secrets: never print them.
    from urllib.parse import urlsplit
    parts = urlsplit(url)
    if parts.scheme != "https" and not (parts.scheme == "http" and parts.hostname in ("127.0.0.1", "localhost")):
        raise RuntimeError("Upload URL must use HTTPS (or an isolated loopback test)")
    # Iterable request body with a fixed Content-Length is streamed by http.client,
    # rather than loading large .pub files wholly into RAM or using chunked framing.
    req = urllib.request.Request(
        url, data=stream_file(path), method="PUT",
        headers={"Content-Type": asset["content_type"], "Content-Length": str(asset["size"])},
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        if resp.status not in (200, 201, 204):
            raise RuntimeError(f"Unexpected PUT response {resp.status}")


def verify_public_url(asset: dict, *, base: str = SITE_BASE, timeout_s: int = 1200) -> dict:
    # Full SHA-256 readback, not ETag (multipart/non-MD5 values aren't a digest).
    rel = asset["library_path"][len(PREFIX) + 1:]
    url = base.rstrip("/") + "/booklets/" + rel
    req = urllib.request.Request(url, method="GET",
                                 headers={"Cache-Control": "no-cache", "Accept-Encoding": "identity"})
    h = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(req, timeout=timeout_s) as response:
        actual_ct = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        expected_ct = asset["content_type"].split(";", 1)[0].strip().lower()
        if actual_ct != expected_ct:
            raise RuntimeError(f"Wrong content-type: {actual_ct}, expected {expected_ct}")
        while True:
            chunk = response.read(BUFFER_SIZE)
            if not chunk:
                break
            h.update(chunk)
            size += len(chunk)
    if size != asset["size"] or h.hexdigest() != asset["sha256"]:
        raise RuntimeError("Public readback size/hash failed")
    return {"size": size, "sha256": h.hexdigest(), "content_type": actual_ct}


def folder_paths(assets: list[dict]) -> list[str]:
    folders = {PREFIX}
    for asset in assets:
        parts = asset["library_path"].strip("/").split("/")
        # Stop at /sites/bhgsite-working, and only return directories underneath /booklets.
        for j in range(3, len(parts)):
            path = "/" + "/".join(parts[:j])
            if path == PREFIX or path.startswith(PREFIX + "/"):
                folders.add(path)
    return sorted(folders, key=lambda x: (x.count("/"), x))


def ensure_folders(api_base: str, token: str, house_id: str, assets: list[dict]) -> None:
    for path in folder_paths(assets):
        try:
            api_json(api_base, token, "POST", f"/api/houses/{house_id}/library/folders",
                     {"path": path + "/"})
        except RuntimeError as exc:
            detail = str(exc).lower()
            if ("http 409" in detail or ("http 400" in detail and "exist" in detail)):
                continue
            raise


def plan(manifest: dict, selected: list[dict], journal: dict) -> dict:
    skipped = [a for a in selected if receipt_matches(a, journal)]
    pending = [a for a in selected if not receipt_matches(a, journal)]
    summary = {
        "title_count": len(set(a["catalog_number"] for a in selected)),
        "asset_count": len(selected),
        "pending": len(pending), "previously_verified": len(skipped),
        "pending_bytes": sum(a["size"] for a in pending),
        "total_bytes": sum(a["size"] for a in selected),
        "mode": "LOCAL PLAN ONLY -- no upload, no authentication",
    }
    return summary


def execute(manifest: dict, selected: list[dict], journal: dict,
            decisions: dict, *, confirm_publication: bool) -> None:
    # Block *all* writes before even acquiring credentials or creating Library folders.
    authorise(decisions, selected, explicit=confirm_publication)
    cfg = load_hou_config()
    if cfg["house_id"] != DEFAULT_HOUSE_ID or cfg["api_base"] != DEFAULT_API_BASE:
        raise RuntimeError("Unexpected BHG House or API host; refusing cross-house release")
    if not cfg["api_key"]:
        raise RuntimeError("No BHG House API key")
    token = exchange_token(cfg["api_base"], cfg["api_key"])
    ensure_folders(cfg["api_base"], token, cfg["house_id"], selected)
    for index, asset in enumerate(selected, 1):
        local = safe_file(WORKSPACE, asset["local_relative"])
        if digest(local) != asset["sha256"]:
            raise RuntimeError(f"Local file has changed: {asset['local_relative']}")
        if receipt_matches(asset, journal):
            print(f"SKIP VERIFIED {index}/{len(selected)} {asset['library_path']}", flush=True)
            continue
        result = api_json(
            cfg["api_base"], token, "POST",
            f"/api/houses/{cfg['house_id']}/library/upload",
            {"path": asset["library_path"], "content_type": asset["content_type"]},
        )
        presigned = result.get("upload_url")
        if not presigned:
            raise RuntimeError("Library API did not return an upload_url")
        upload_stream(presigned, asset, local)
        # A partial failure isn't marked complete. Subsequent invocation safely retries.
        checked = verify_public_url(asset)
        journal["verified"][asset["library_path"]] = {
            "sha256": asset["sha256"], "size": checked["size"],
            "content_type": checked["content_type"], "public_bytes_verified": True,
            "verified_at_epoch": round(time.time()),
        }
        atomic_json(JOURNAL_PATH, journal)
        print(f"VERIFIED {index}/{len(selected)} {asset['library_path']}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--titles", type=int, nargs="+", required=True)
    parser.add_argument("--kinds", choices=sorted(FORMAT_NAMES), nargs="+", required=True)
    parser.add_argument("--execute", action="store_true", help="Public upload, only after explicit rights approval")
    parser.add_argument("--confirm-publication", action="store_true", help="Confirm these files will be public")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate(manifest, WORKSPACE, verify_bytes=False)
    selected = select(manifest, args.titles, args.kinds)
    decisions = ensure_decisions(manifest, APPROVALS_PATH)
    if args.execute:
        with exclusive_transfer_lock(RELEASE_DIR / "upload.lock"):
            journal = load_journal(JOURNAL_PATH, manifest)
            result = plan(manifest, selected, journal)
            print(json.dumps(result, indent=2), flush=True)
            execute(manifest, selected, journal, decisions, confirm_publication=args.confirm_publication)
    else:
        journal = load_journal(JOURNAL_PATH, manifest)
        print(json.dumps(plan(manifest, selected, journal), indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
