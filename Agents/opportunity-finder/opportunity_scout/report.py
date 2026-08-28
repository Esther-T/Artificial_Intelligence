from __future__ import annotations

from datetime import date
from pathlib import Path

from .models import RankedOpportunity


def render_report(opportunities: list[RankedOpportunity], run_date: date) -> str:
    lines = [
        f"# Opportunity report — {run_date.isoformat()}",
        "",
        "> Automated triage only. Confirm eligibility, price, and deadlines at the linked source.",
        "",
    ]
    if not opportunities:
        lines.append("No new opportunities met the relevance threshold today.")
        return "\n".join(lines) + "\n"

    for index, opportunity in enumerate(opportunities, start=1):
        candidate = opportunity.candidate
        lines.extend(
            [
                f"## {index}. [{candidate.title}]({candidate.url})",
                "",
                f"- **Score:** {opportunity.score:.2f}/10",
                f"- **Confidence:** {opportunity.confidence}",
                f"- **Eligibility:** {opportunity.eligibility}",
                f"- **Estimated value:** {opportunity.estimated_value}",
                f"- **Deadline:** {opportunity.deadline}",
                f"- **Source:** {candidate.source or 'Not provided'}",
                f"- **Why it ranked:** {'; '.join(opportunity.reasons)}",
                f"- **Next action:** {opportunity.next_action}",
                "",
                candidate.summary or "No source summary was available.",
                "",
            ]
        )
    return "\n".join(lines)


def save_report(directory: Path, report: str, run_date: date) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{run_date.isoformat()}.md"
    path.write_text(report, encoding="utf-8")
    return path

