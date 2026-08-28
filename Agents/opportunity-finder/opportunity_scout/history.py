from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import Candidate, RankedOpportunity


TRACKING_PARAMETERS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMETERS
    ]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))


def opportunity_id(candidate: Candidate) -> str:
    return hashlib.sha256(canonical_url(candidate.url).encode("utf-8")).hexdigest()[:20]


def load_history(path: Path) -> dict:
    if not path.exists():
        return {"items": {}}
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    value.setdefault("items", {})
    return value


def unseen(candidates: list[Candidate], history: dict) -> list[Candidate]:
    known = history.get("items", {})
    deduplicated: dict[str, Candidate] = {}
    for candidate in candidates:
        item_id = opportunity_id(candidate)
        if item_id not in known:
            deduplicated[item_id] = candidate
    return list(deduplicated.values())


def update_history(history: dict, opportunities: list[RankedOpportunity]) -> dict:
    now = datetime.now(UTC).isoformat()
    items = history.setdefault("items", {})
    for opportunity in opportunities:
        item_id = opportunity_id(opportunity.candidate)
        previous = items.get(item_id, {})
        items[item_id] = {
            "title": opportunity.candidate.title,
            "url": canonical_url(opportunity.candidate.url),
            "first_seen": previous.get("first_seen", now),
            "last_seen": now,
            "last_score": opportunity.score,
        }
    return history


def save_history(path: Path, history: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

