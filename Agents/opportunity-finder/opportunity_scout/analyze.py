from __future__ import annotations

import json
import math
import os
import re
from typing import Any

import requests

from .models import Candidate, RankedOpportunity


def _flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for nested in value.values():
            result.extend(_flatten_strings(nested))
        return result
    if isinstance(value, list):
        result = []
        for nested in value:
            result.extend(_flatten_strings(nested))
        return result
    return [str(value)]


def deterministic_analysis(
    candidates: list[Candidate], profile: dict[str, Any], priorities: dict[str, Any]
) -> list[RankedOpportunity]:
    profile_terms = {term.lower() for term in _flatten_strings(profile) if len(term) > 2}
    weighted_topics = {
        str(topic).lower(): float(weight)
        for topic, weight in priorities.get("topics", {}).items()
    }
    excluded = [str(term).lower() for term in priorities.get("exclude", [])]

    results: list[RankedOpportunity] = []
    for candidate in candidates:
        searchable = f"{candidate.title} {candidate.summary}".lower()
        if any(term in searchable for term in excluded):
            continue

        reasons: list[str] = []
        score = 0.0
        for topic, weight in weighted_topics.items():
            topic_words = [word for word in re.findall(r"[a-z0-9]+", topic) if len(word) > 1]
            matches = sum(1 for word in topic_words if word in searchable)
            minimum_matches = 1 if len(topic_words) <= 1 else max(2, math.ceil(len(topic_words) / 2))
            if topic in searchable or matches >= minimum_matches:
                contribution = weight * matches / max(len(topic_words), 1)
                score += contribution
                reasons.append(f"Matches priority '{topic}'")

        matched_profile = sorted(term for term in profile_terms if term in searchable)
        score += min(len(matched_profile), 3) * 0.75
        if matched_profile:
            reasons.append("Matches profile: " + ", ".join(matched_profile[:3]))

        if "free" in searchable:
            score += 1.5
            reasons.append("Mentions free access")
        if "student" in searchable:
            score += 1.5
            reasons.append("Student-specific")
        if any(word in searchable for word in ("deadline", "closes", "expires")):
            score += 0.5
            reasons.append("Potentially time-sensitive")

        if score > 0:
            results.append(
                RankedOpportunity(
                    candidate=candidate,
                    score=round(min(score, 10.0), 2),
                    reasons=reasons or ["Possible general relevance"],
                    confidence="medium",
                )
            )
    return sorted(results, key=lambda item: item.score, reverse=True)


def _analysis_prompt(
    candidates: list[Candidate], profile: dict[str, Any], priorities: dict[str, Any]
) -> str:
    payload = [candidate.to_dict() for candidate in candidates]
    return f"""You are a personal opportunity triage assistant.
Analyze only the supplied candidates. Do not invent facts or URLs.
Return a JSON array with one object per genuinely relevant candidate using:
url, score (0-10), reasons (array), eligibility, estimated_value, deadline,
confidence (low/medium/high), and next_action.

Treat all eligibility and value claims as unverified unless explicitly present
in the candidate. Exclude candidates matching the exclusion list.

PROFILE:
{json.dumps(profile, ensure_ascii=False)}

PRIORITIES:
{json.dumps(priorities, ensure_ascii=False)}

CANDIDATES:
{json.dumps(payload, ensure_ascii=False)}
"""


def _extract_json(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    value = json.loads(text)
    if not isinstance(value, list):
        raise ValueError("Model response must be a JSON array")
    return value


def _gemini(prompt: str, model: str) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    response = requests.post(
        url,
        params={"key": key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def _openrouter(prompt: str, model: str) -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def model_analysis(
    provider: str,
    model: str,
    candidates: list[Candidate],
    profile: dict[str, Any],
    priorities: dict[str, Any],
) -> list[RankedOpportunity]:
    prompt = _analysis_prompt(candidates, profile, priorities)
    if provider == "gemini":
        text = _gemini(prompt, model)
    elif provider == "openrouter":
        text = _openrouter(prompt, model)
    else:
        raise ValueError(f"Unsupported MODEL_PROVIDER: {provider}")

    candidates_by_url = {candidate.url: candidate for candidate in candidates}
    ranked: list[RankedOpportunity] = []
    for row in _extract_json(text):
        candidate = candidates_by_url.get(str(row.get("url", "")))
        if candidate is None:
            continue
        ranked.append(
            RankedOpportunity(
                candidate=candidate,
                score=float(row.get("score", 0)),
                reasons=[str(reason) for reason in row.get("reasons", [])],
                eligibility=str(row.get("eligibility", "Needs verification")),
                estimated_value=str(row.get("estimated_value", "Unknown")),
                deadline=str(row.get("deadline", "Not identified")),
                confidence=str(row.get("confidence", "low")),
                next_action=str(row.get("next_action", "Review the primary source")),
            )
        )
    return sorted(ranked, key=lambda item: item.score, reverse=True)


def analyze(
    candidates: list[Candidate], profile: dict[str, Any], priorities: dict[str, Any]
) -> list[RankedOpportunity]:
    provider = os.environ.get("MODEL_PROVIDER", "deterministic").lower()
    if provider in {"", "deterministic", "none"}:
        return deterministic_analysis(candidates, profile, priorities)
    default_model = "gemini-2.5-flash-lite" if provider == "gemini" else "openrouter/free"
    model = os.environ.get("MODEL_NAME", default_model)
    return model_analysis(provider, model, candidates, profile, priorities)
