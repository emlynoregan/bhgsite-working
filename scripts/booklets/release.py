"""BHG Working-only publication readiness; no network calls or writes."""
from __future__ import annotations
import json
from pathlib import Path
from .assets import PREFIX, WORKSPACE

RELEASE = WORKSPACE / "booklet-release"
MANIFEST = RELEASE / "asset-manifest.json"
DECISIONS = RELEASE / "publication-decisions.json"
JOURNAL = RELEASE / "upload-journal-recovered.json"
FORMATS = ("reader", "pdf", "publisher")


def ready() -> tuple[bool, str]:
    if not all(p.is_file() for p in (MANIFEST, DECISIONS, JOURNAL)):
        return False, "Missing manifest, approval or transfer receipt file"
    try:
        from .assets import validate
        m=json.loads(MANIFEST.read_text(encoding="utf8"))
        d=json.loads(DECISIONS.read_text(encoding="utf8"))
        j=json.loads(JOURNAL.read_text(encoding="utf8"))
        validate(m, WORKSPACE, verify_bytes=False)
        if m["destination"]!=PREFIX or d.get("destination")!=PREFIX or j.get("destination")!=PREFIX:
            return False, "Unapproved destination"
        if m["manifest_sha256"]!=d.get("manifest_sha256"):
            return False, "Manifest approval mismatch"
        if not d.get("publication_authorised") or not d.get("approval_reference"):
            return False, "Publication permission absent"
        count={}
        for a in m["assets"]:
            n=str(a["catalog_number"])
            if d.get("approved_title_formats",{}).get(n,{}).get(a["kind"]) is not True:
                return False, f"Not approved {n}/{a['kind']}"
            receipt=j.get("verified",{}).get(a["library_path"],{})
            if receipt.get("sha256")!=a["sha256"] or receipt.get("size")!=a["size"] or receipt.get("public_bytes_verified") is not True:
                return False, f"Missing public verification: {a['library_path']}"
            count.setdefault(n,set()).add(a["kind"])
        if len(m["assets"])!=800 or len(count)!=38 or any(set(FORMATS)!=v for v in count.values()):
            return False, "Incomplete 38-title release"
        return True, f"Verified {len(m['assets'])} Working Library assets"
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return False, f"Invalid release state: {exc}"
