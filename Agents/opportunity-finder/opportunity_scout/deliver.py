from __future__ import annotations

import os

import requests


def deliver_webhook(report: str) -> bool:
    webhook = os.environ.get("DELIVERY_WEBHOOK")
    if not webhook:
        return False
    response = requests.post(webhook, json={"content": report[:1900]}, timeout=30)
    response.raise_for_status()
    return True


def append_github_summary(report: str) -> bool:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return False
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write(report)
    return True

