#!/usr/bin/env python3
"""
Generate README.md from public/data/intern_data.json.

Design goals (per repo usage + UX):
- Keep it simple: remove summary/leaderboard/hot/extra sections.
- Show the main thing users care about: which companies are active and what stage signals exist.
- Sort newest -> oldest everywhere (by Last Active date).

Run:
  python scripts/generate_readme.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "public" / "data" / "intern_data.json"
OUT_PATH = ROOT / "README.md"

IS_URL = "https://interviewsense.org"
IS_DASH = "https://interviewsense.org/dashboard"
PREP_BADGE = "https://img.shields.io/badge/Prep-4F5BD5?style=flat-square&logoColor=white"


def prep_link(company: str) -> str:
    slug = company.lower().replace(" ", "-").replace("&", "and")
    return f"[![Prep]({PREP_BADGE})]({IS_DASH}?company={slug})"


def last_active(company_obj: dict) -> str:
    daily = company_obj.get("daily") or []
    if not daily:
        # Fallback to whatever message samples we have for that company.
        msgs = company_obj.get("messages") or []
        return max((m.get("date", "") for m in msgs), default="")
    # daily is already date-sorted in our data, but don’t assume.
    return max((d.get("date", "") for d in daily), default="")


def bucket(company_obj: dict) -> str:
    stages = company_obj.get("stages") or {}
    if int(stages.get("offer", 0)) > 0:
        return "Offers"
    if int(stages.get("interview", 0)) > 0:
        return "Interviewing"
    if int(stages.get("oa", 0)) > 0:
        return "OA"
    return "Active"


def main() -> int:
    data = json.loads(DATA_PATH.read_text())
    companies = data.get("companies") or []
    generated = data.get("generated") or ""
    stats = data.get("stats") or {}
    total_msgs = int(stats.get("total_process_msgs") or 0)
    total_cos = int(stats.get("total_companies_tracked") or 0)
    total_offers = int(stats.get("total_offers") or 0)
    total_ints = int(stats.get("total_interviews") or 0)
    total_oas = int(stats.get("total_oas") or 0)
    total_rejs = int(stats.get("total_rejections") or 0)

    rows = []
    for c in companies:
        rows.append(
            {
                "name": c.get("name", ""),
                "offers": int((c.get("stages") or {}).get("offer", 0)),
                "interviews": int((c.get("stages") or {}).get("interview", 0)),
                "oas": int((c.get("stages") or {}).get("oa", 0)),
                "last": last_active(c),
                "bucket": bucket(c),
            }
        )

    # Newest -> oldest, then more signal.
    rows.sort(key=lambda r: (r["last"], r["offers"], r["interviews"], r["oas"], r["name"].lower()), reverse=True)

    now_utc = datetime.now(timezone.utc).strftime("%b %d, %Y %H:%M UTC")

    lines: list[str] = []
    lines += [
        "# 🧠 Summer 2026 Offer & Interview Reports",
        "",
        "Track where candidates are reporting Summer 2026 offers, interviews, online assessments, and rejections across software, data science, quant, AI, hardware, and more.",
        "",
        "Maintained from Discord `!process` reports and paired with InterviewSense so you can prep around the companies that are actually moving right now.",
        "",
        f"![Updated](https://img.shields.io/badge/updated-{now_utc.replace(' ','%20').replace(',','').replace(':','%3A')}-4F5BD5?style=flat-square) "
        f"![Reports](https://img.shields.io/badge/reports-{total_msgs:,}-4F5BD5?style=flat-square) "
        f"![Companies](https://img.shields.io/badge/companies-{total_cos}-4F5BD5?style=flat-square) "
        f"![Offers](https://img.shields.io/badge/offers-{total_offers}-22c55e?style=flat-square) "
        f"![Interviews](https://img.shields.io/badge/interviews-{total_ints:,}-4F5BD5?style=flat-square) "
        f"![OAs](https://img.shields.io/badge/OAs-{total_oas:,}-4F5BD5?style=flat-square) "
        f"![Rejections](https://img.shields.io/badge/rejections-{total_rejs:,}-ef4444?style=flat-square)",
        "",
        "🧠 For practical tips on navigating the internship process, check out the guide: [Zero to Offer](ZERO_TO_OFFER.md)",
        "",
        "🙏 Contribute by submitting an [issue](https://github.com/interviewsense/2026-Summer-Intern-Process-Tracker/issues). See the contribution guidelines [here](CONTRIBUTING.md).",
        "",
        "---",
        "",
        f"## Browse {total_msgs:,} Process Reports by Signal",
        "",
        f"🎉 **Offer reports** ({total_offers:,})",
        "",
        f"🎙️ **Interview reports** ({total_ints:,})",
        "",
        f"📝 **OA mentions** ({total_oas:,})",
        "",
        f"💀 **Rejection reports** ({total_rejs:,})",
        "",
        "---",
        "",
        '<p align="center"><strong>😤 Struggling with interviews at these companies?</strong></p>',
        "",
        f'<p align="center"><a href="{IS_URL}"><strong>Get AI mock interviews built around every company in this list</strong></a></p>',
        "",
        '<p align="center"><img src="assets/cta-small.png" alt="InterviewSense" width="220" /></p>',
        "",
        f'<p align="center"><a href="{IS_URL}"><img src="https://img.shields.io/badge/Start%20Free%20on%20InterviewSense-4F5BD5?style=for-the-badge&logoColor=white" alt="Start Free on InterviewSense" /></a></p>',
        "",
        "<p align=\"center\"><em>Stop grinding random LeetCode. InterviewSense builds mock interviews around the real offer, OA, and interview patterns candidates are reporting right now.</em></p>",
        "",
        "---",
        "",
        "## 📡 Companies (Newest → Oldest)",
        "",
        "| Company | Offers | Interviews | OAs | Last Active | Prep |",
        "|---------|--------|------------|-----|-------------|------|",
    ]

    for r in rows:
        if not r["name"]:
            continue
        lines.append(
            f"| **{r['name']}** | `{r['offers']}` | `{r['interviews']}` | `{r['oas']}` | `{r['last']}` | {prep_link(r['name'])} |"
        )

    lines += [
        "",
        f"*Last data build: {generated}.*",
    ]

    OUT_PATH.write_text("\n".join(lines) + "\n")
    print(f"README written to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
