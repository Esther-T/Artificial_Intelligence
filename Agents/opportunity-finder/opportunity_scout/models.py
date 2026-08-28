from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class Candidate:
    title: str
    url: str
    summary: str = ""
    source: str = ""
    published_at: str = ""

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Candidate":
        return cls(
            title=str(value.get("title", "")).strip(),
            url=str(value.get("url", "")).strip(),
            summary=str(value.get("summary", "")).strip(),
            source=str(value.get("source", "")).strip(),
            published_at=str(value.get("published_at", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RankedOpportunity:
    candidate: Candidate
    score: float
    reasons: list[str]
    eligibility: str = "Needs verification"
    estimated_value: str = "Unknown"
    deadline: str = "Not identified"
    confidence: str = "medium"
    next_action: str = "Review the primary source"

