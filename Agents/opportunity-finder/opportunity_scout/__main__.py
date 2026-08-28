from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .analyze import analyze
from .collect import collect_feeds, collect_sample
from .config import load_yaml
from .deliver import append_github_summary, deliver_webhook
from .history import load_history, save_history, unseen, update_history
from .report import render_report, save_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the personal opportunity scout")
    parser.add_argument("--dry-run", action="store_true", help="Use included sample candidates")
    parser.add_argument("--no-save", action="store_true", help="Do not change reports or history")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    profile = load_yaml(root / "config" / "profile.yml")
    priorities = load_yaml(root / "config" / "priorities.yml")
    sources = load_yaml(root / "config" / "sources.yml")
    history_path = root / "data" / "seen-opportunities.json"
    history = load_history(history_path)

    if args.dry_run:
        candidates = collect_sample(root / "examples" / "sample_candidates.json")
        # A dry run should remain repeatable even after a saved dry-run report.
        candidates_to_analyze = candidates
    else:
        candidates = collect_feeds(sources)
        candidates_to_analyze = unseen(candidates, history)

    opportunities = analyze(candidates_to_analyze, profile, priorities)
    maximum_results = int(priorities.get("maximum_results", 10))
    opportunities = opportunities[:maximum_results]
    today = date.today()
    report = render_report(opportunities, today)
    print(report)

    if not args.no_save:
        report_path = save_report(root / "reports", report, today)
        save_history(history_path, update_history(history, opportunities))
        append_github_summary(report)
        deliver_webhook(report)
        print(f"Saved report: {report_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

