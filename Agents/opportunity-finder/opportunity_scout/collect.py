from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

from .models import Candidate


def collect_sample(path: Path) -> list[Candidate]:
    with path.open("r", encoding="utf-8") as handle:
        rows = json.load(handle)
    return [Candidate.from_dict(row) for row in rows]


def _text(element: ET.Element | None) -> str:
    return "" if element is None or element.text is None else element.text.strip()


def _first(element: ET.Element, names: tuple[str, ...]) -> ET.Element | None:
    for child in element.iter():
        local_name = child.tag.rsplit("}", 1)[-1].lower()
        if local_name in names:
            return child
    return None


def _parse_feed(content: bytes, feed_url: str, limit: int) -> list[Candidate]:
    root = ET.fromstring(content)
    entries = [
        element
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1].lower() in {"item", "entry"}
    ]
    candidates: list[Candidate] = []
    for entry in entries[:limit]:
        title = _text(_first(entry, ("title",)))
        summary = _text(_first(entry, ("summary", "description", "content")))
        published = _text(_first(entry, ("published", "updated", "pubdate")))
        link_element = _first(entry, ("link",))
        link = ""
        if link_element is not None:
            link = link_element.attrib.get("href", "") or _text(link_element)
        if title and link:
            candidates.append(
                Candidate(
                    title=title,
                    url=urljoin(feed_url, link),
                    summary=summary,
                    source=feed_url,
                    published_at=published,
                )
            )
    return candidates


def collect_feeds(source_config: dict[str, Any]) -> list[Candidate]:
    settings = source_config.get("collection", {})
    timeout = int(settings.get("timeout_seconds", 20))
    per_feed = int(settings.get("maximum_items_per_feed", 25))
    maximum = int(settings.get("maximum_candidates_per_run", 100))

    candidates: list[Candidate] = []
    headers = {"User-Agent": "PersonalOpportunityScout/0.1 (private research)"}
    for feed_url in source_config.get("feeds", []):
        response = requests.get(feed_url, timeout=timeout, headers=headers)
        response.raise_for_status()
        candidates.extend(_parse_feed(response.content, feed_url, per_feed))
        if len(candidates) >= maximum:
            break
    return candidates[:maximum]

