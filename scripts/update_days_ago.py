#!/usr/bin/env python3
"""
update_days_ago.py
Rewrites every "Last Active" date in the Live Status Board tables
and every "When" date in the Recent Offers table from absolute dates
(2026-03-XX) to relative labels (today / 1 day ago / N days ago).

Run automatically via the pre-push git hook, or manually:
    python3 scripts/update_days_ago.py
"""

import re
import sys
from datetime import date, datetime
from pathlib import Path

README = Path(__file__).parent.parent / "README.md"
TODAY = date.today()


def to_relative(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' to a human-readable relative label."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return date_str
    delta = (TODAY - d).days
    if delta == 0:
        return "today"
    if delta == 1:
        return "1 day ago"
    return f"{delta} days ago"


def replace_dates(text: str) -> str:
    # Match bare ISO dates inside backticks: `2026-03-16`
    def repl(m):
        return f"`{to_relative(m.group(1))}`"

    return re.sub(r"`(\d{4}-\d{2}-\d{2})`", repl, text)


def main():
    if not README.exists():
        print(f"ERROR: README not found at {README}", file=sys.stderr)
        sys.exit(1)

    original = README.read_text(encoding="utf-8")
    updated = replace_dates(original)

    if updated == original:
        print("update_days_ago: no date changes needed.")
        return

    README.write_text(updated, encoding="utf-8")
    changed = sum(
        1
        for a, b in zip(original.splitlines(), updated.splitlines())
        if a != b
    )
    print(f"update_days_ago: updated {changed} date(s) to relative labels.")


if __name__ == "__main__":
    main()
