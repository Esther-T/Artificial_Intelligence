from __future__ import annotations

import unittest
from datetime import date

from opportunity_scout.analyze import deterministic_analysis
from opportunity_scout.history import canonical_url, opportunity_id, unseen
from opportunity_scout.models import Candidate
from opportunity_scout.report import render_report


class PipelineTests(unittest.TestCase):
    def test_tracking_parameters_are_removed(self) -> None:
        actual = canonical_url("HTTPS://Example.COM/offer/?utm_source=test&code=student#top")
        self.assertEqual(actual, "https://example.com/offer?code=student")

    def test_seen_candidate_is_filtered(self) -> None:
        candidate = Candidate(title="Free student tool", url="https://example.com/tool")
        history = {"items": {opportunity_id(candidate): {"title": candidate.title}}}
        self.assertEqual(unseen([candidate], history), [])

    def test_excluded_topic_is_removed(self) -> None:
        candidates = [
            Candidate(title="Free student AI tool", url="https://example.com/ai"),
            Candidate(title="Casino welcome bonus", url="https://example.com/casino"),
        ]
        profile = {"status": {"student": True}}
        priorities = {"topics": {"free AI tools": 5}, "exclude": ["casino"]}
        ranked = deterministic_analysis(candidates, profile, priorities)
        self.assertEqual([item.candidate.url for item in ranked], ["https://example.com/ai"])

    def test_report_contains_source_link(self) -> None:
        candidate = Candidate(title="Student benefit", url="https://example.com/benefit")
        ranked = deterministic_analysis(
            [candidate], {"status": {"student": True}}, {"topics": {"student benefit": 5}}
        )
        report = render_report(ranked, date(2026, 8, 27))
        self.assertIn("[Student benefit](https://example.com/benefit)", report)


if __name__ == "__main__":
    unittest.main()

