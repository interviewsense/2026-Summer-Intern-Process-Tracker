#!/usr/bin/env python3
"""
Merge additional Discord CSV exports into the existing public/data/intern_data.json.

Why this exists:
- We don't always have the original "base" export folder locally anymore.
- We still want to layer new exports on top without destroying the existing dataset.

Run:
  python scripts/merge_imports.py /path/to/export_dir1 /path/to/export_dir2

Notes:
- This intentionally only *adds* to company counts/daily/messages/threads when we can
  confidently match a company. It never deletes existing data.
- Dedupe is best-effort: since the stored JSON doesn't include message IDs, we dedupe
  by (date, author, content) fingerprints.
"""

from __future__ import annotations

import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUT_PATH = Path(__file__).resolve().parent.parent / "public" / "data" / "intern_data.json"


COMPANIES: dict[str, list[str]] = {
    # Big Tech / AI
    "amazon": ["amazon", " zon ", "zon "],
    "google": ["google", "goog "],
    "microsoft": ["microsoft", "msft"],
    "meta": ["meta ", " meta,", "facebook"],
    "apple": ["apple"],
    "netflix": ["netflix"],
    "openai": ["openai", "open ai", " oai "],
    "xai": [" xai "],
    "anthropic": ["anthropic"],
    "alibaba": ["alibaba"],
    "tiktok": ["tiktok", "tik tok", "bytedance", "byte dance"],
    "bytedance": ["bytedance", "byte dance"],
    "notion": ["notion"],
    "verkada": ["verkada"],
    "brex": ["brex"],
    "bloomberg": ["bloomberg"],
    # Quant / Finance
    "citadel": ["citadel"],
    "jane street": ["jane street"],
    "optiver": ["optiver"],
    "two sigma": ["two sigma", " 2sig ", "2sigma"],
    "hrt": [" hrt "],
    "drw": [" drw "],
    "imc": [" imc "],
    "virtu": ["virtu "],
    "akuna": ["akuna"],
    "bridgewater": ["bridgewater"],
    "sig": [" sig "],
    "cit sec": ["citsec", "cit sec"],
    "goldman sachs": ["goldman", "goldman sachs"],
    "wells fargo": ["wells fargo", "wells "],
    "point72": ["point72", " p72 "],
    "arrowstreet capital": ["arrowstreet"],
    # SaaS / hardware / other
    "nvidia": ["nvidia"],
    "amd": [" amd "],
    "intel": ["intel "],
    "qualcomm": ["qualcomm"],
    "salesforce": ["salesforce"],
    "snowflake": ["snowflake"],
    "stripe": ["stripe"],
    "ramp": ["ramp "],
    "coinbase": ["coinbase"],
    "cloudflare": ["cloudflare"],
    "dropbox": ["dropbox"],
    "linkedin": ["linkedin"],
    "airbnb": ["airbnb"],
    "uber": ["uber "],
    "lyft": ["lyft "],
    "doordash": ["doordash"],
    "instacart": ["instacart"],
    "pinterest": ["pinterest"],
    "reddit": ["reddit "],
    "roblox": ["roblox"],
    "shopify": ["shopify"],
    "intuit": ["intuit"],
    "oracle": ["oracle"],
    "ibm": ["ibm"],
    "visa": ["visa "],
    "capital one": [" c1 ", "capital one", "cap1"],
    "palantir": ["palantir"],
    "scale ai": ["scale ai", "scaleai"],
    "snapchat": ["snap ", "snapchat"],
    "ebay": ["ebay"],
    "paypal": ["paypal"],
    "hubspot": ["hubspot"],
    "okta": ["okta "],
    "mongodb": ["mongodb"],
    "github": ["github "],
    "klaviyo": ["klaviyo"],
    "rippling": ["rippling"],
    "box": [" box "],
    "patreon": ["patreon"],
    "robinhood": ["robinhood"],
    "sofi": ["sofi "],
    "handshake": ["handshake"],
    "harvey": ["harvey "],
    "tesla": ["tesla"],
    "spacex": ["spacex"],
    "rivian": ["rivian"],
    "zoox": ["zoox"],
    "neuralink": ["neuralink"],
    "sierra space": ["sierra space", "sierra "],
    "aurora": ["aurora "],
    "nuro": ["nuro "],
    "arm": [" arm "],
    "asml": ["asml"],
    "ericsson": ["ericsson"],
    "nokia": ["nokia"],
    "disney": ["disney"],
    "riot games": ["riot "],
    "expedia": ["expedia"],
    "walmart": ["walmart"],
    "cvs": [" cvs "],
    "at&t": ["at&t"],
    "cisco": ["cisco "],
    "docusign": ["docusign"],
    "geico": ["geico"],
    "crowdstrike": ["crowdstrike"],
    "pure storage": ["pure storage", "pure "],
    "palo alto networks": ["palo alto networks", "palo alto", "palo "],
    "ziprecruiter": ["ziprecruiter"],
    "mathworks": ["mathworks"],
    "together ai": ["together ai", "together "],
    "gemini": ["gemini "],
    # From the add-on folders people explicitly mention
    "analysis group": ["analysis group"],
    "fifth third bank": ["fifth third"],
    "hp": [" hp "],
    "jump": [" jump "],
    "texas instruments": ["texas instruments", " ti "],
    "rocket lab": ["rocket lab", "rocketlab"],
    "waymo": ["waymo"],
}


STAGE_PATTERNS: dict[str, list[str]] = {
    "offer": ["offer", "accepted", "signed offer", "verbal offer", "got the offer", "got an offer"],
    "rejection": ["reject", " rej ", "rej'd", "denied", "no offer", "ghosted", "got rejected", "rescind", "rescinded"],
    "interview": [
        "interview",
        "round 1",
        "round 2",
        " round 3",
        " r1 ",
        " r2 ",
        " r3 ",
        "behavioral",
        "technical",
        "phone screen",
        "virtual onsite",
        "onsite",
        "hiring manager",
        "hm call",
        "final round",
        "recruiter screen",
        "screen call",
    ],
    "oa": ["oa ", "online assessment", "hackerrank", "codility", "codesignal", "coding assessment", "take home"],
}


def parse_date(d: str) -> str:
    return d[:10] if d else ""


def detect_stage(content: str) -> str:
    c = content.lower()
    for stage, kws in STAGE_PATTERNS.items():
        if any(k in c for k in kws):
            return stage
    return "question"


def match_company(text: str) -> str | None:
    c = " " + (text or "").lower() + " "
    for company, kws in COMPANIES.items():
        if any(k in c for k in kws):
            return company
    return None


def clean_process_content(content: str) -> str:
    content = re.sub(r"<@!?\d+>", "", content or "")
    content = content.split("\n")[0].strip()
    return content


def fingerprint(msg: dict[str, Any]) -> tuple[str, str, str]:
    return (
        msg.get("date", "")[:10],
        (msg.get("author", "") or "").strip().lower(),
        (msg.get("content", "") or "").strip().lower(),
    )


def load_export_dir(export_dir: str) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    # Returns (main_process_msgs, thread_rows_by_title)
    export_dir = os.path.abspath(export_dir)
    main_msgs: list[dict[str, Any]] = []
    thread_rows: dict[str, list[dict[str, Any]]] = {}

    main_csvs = sorted(glob.glob(os.path.join(export_dir, "*_summer_intern_process_page_*.csv")))
    for f in main_csvs:
        with open(f, encoding="utf-8") as fp:
            for row in csv.DictReader(fp):
                content = row.get("content", "") or ""
                if not content.lower().startswith("!process"):
                    continue
                main_msgs.append(row)

    thread_csvs = sorted(glob.glob(os.path.join(export_dir, "!process*.csv")))
    for f in thread_csvs:
        title = os.path.basename(f).replace("_page_1.csv", "")
        with open(f, encoding="utf-8") as fp:
            thread_rows[title] = list(csv.DictReader(fp))

    return main_msgs, thread_rows


def ensure_company_obj(base: dict[str, Any], name: str) -> dict[str, Any]:
    for c in base["companies"]:
        if c["name"].lower() == name.lower():
            return c
    obj = {
        "name": name,
        "count": 0,
        "stages": {"offer": 0, "rejection": 0, "interview": 0, "oa": 0, "question": 0},
        "messages": [],
        "threads": [],
        "daily": [],
    }
    base["companies"].append(obj)
    return obj


def bump_daily(company_obj: dict[str, Any], date: str) -> None:
    if not date:
        return
    for d in company_obj.get("daily", []):
        if d.get("date") == date:
            d["count"] = int(d.get("count", 0)) + 1
            return
    company_obj.setdefault("daily", []).append({"date": date, "count": 1})


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python scripts/merge_imports.py /path/to/export1 [/path/to/export2 ...]")
        return 2

    if not OUT_PATH.exists():
        print(f"Missing {OUT_PATH}")
        return 1

    base = json.loads(OUT_PATH.read_text())
    base.setdefault("companies", [])
    base.setdefault("recent", [])
    base.setdefault("timeline", [])
    base.setdefault("stats", {})
    old_stats = dict(base.get("stats") or {})
    old_total_process = int(old_stats.get("total_process_msgs") or 0)
    old_total_companies = int(old_stats.get("total_companies_tracked") or 0)
    old_total_offers = int(old_stats.get("total_offers") or 0)
    old_total_rejs = int(old_stats.get("total_rejections") or 0)
    old_total_ints = int(old_stats.get("total_interviews") or 0)
    old_total_oas = int(old_stats.get("total_oas") or 0)

    # Build a fingerprint set to avoid obvious duplicates.
    seen = set()
    for c in base["companies"]:
        for m in c.get("messages", []):
            seen.add(fingerprint(m))
    for r in base.get("recent", []):
        seen.add(fingerprint(r))

    added = 0
    for export_dir in argv[1:]:
        main_msgs, thread_rows = load_export_dir(export_dir)

        for row in main_msgs:
            content = clean_process_content(row.get("content", ""))
            date = parse_date(row.get("date", ""))
            author = row.get("author.global_name", "") or row.get("author.username", "") or ""
            stage = detect_stage(content)
            co = match_company(content)
            if not co:
                continue
            key = fingerprint({"content": content, "date": date, "author": author})
            if key in seen:
                continue
            seen.add(key)
            added += 1

            company_obj = ensure_company_obj(base, co.title() if co.islower() else co)
            company_obj["count"] += 1
            company_obj["stages"][stage] = int(company_obj["stages"].get(stage, 0)) + 1
            bump_daily(company_obj, date)

            # Keep a small sample of messages per company for the UI
            msgs = company_obj.setdefault("messages", [])
            if len(msgs) < 30:
                msgs.append({"content": content[:280], "date": date, "author": author, "stage": stage})

            # Keep recent feed as well (cap later)
            base["recent"].append({"content": content[:200], "company": company_obj["name"], "stage": stage, "date": date, "author": author})

        # Threads: attach by thread title match
        for title, rows in thread_rows.items():
            co = match_company(title)
            if not co:
                continue
            company_obj = ensure_company_obj(base, co.title() if co.islower() else co)
            convo = []
            for r in rows:
                c = r.get("content", "") or ""
                if not c:
                    continue
                convo.append({
                    "content": clean_process_content(c)[:400],
                    "date": parse_date(r.get("date", "")),
                    "author": r.get("author.global_name", "") or r.get("author.username", "") or "",
                })
            if convo:
                company_obj.setdefault("threads", []).append({"title": title.replace("!process ", ""), "messages": convo})

    # Re-sort daily arrays and messages newest->oldest for display
    for c in base["companies"]:
        c["daily"] = sorted(c.get("daily", []), key=lambda x: x.get("date", ""))
        c["messages"] = sorted(c.get("messages", []), key=lambda x: x.get("date", ""), reverse=True)

    base["companies"] = sorted(base["companies"], key=lambda x: (-int(x.get("count", 0)), x.get("name", "").lower()))

    base["recent"] = sorted(base.get("recent", []), key=lambda x: x.get("date", ""), reverse=True)
    base["recent"] = base["recent"][:200]

    # Stats: do NOT attempt a full recount (the stored JSON doesn't contain every raw message),
    # just ensure we never shrink and we only add what we saw in these imports.
    offers_added = 0
    rejs_added = 0
    ints_added = 0
    oas_added = 0
    total_added = 0
    for r in base.get("recent", [])[:added]:
        # best-effort; recent contains a slice, so don't rely on it for totals
        pass
    # We tracked how many new unique fingerprints we appended.
    total_added = added
    # Stage totals added are computed during the merge loop by bumping company stages.
    # Derive those deltas by summing stage counts beyond the old totals, but never shrink.
    offers_now = sum(int(c["stages"].get("offer", 0)) for c in base["companies"])
    rejs_now = sum(int(c["stages"].get("rejection", 0)) for c in base["companies"])
    ints_now = sum(int(c["stages"].get("interview", 0)) for c in base["companies"])
    oas_now = sum(int(c["stages"].get("oa", 0)) for c in base["companies"])

    offers_added = max(0, offers_now - old_total_offers)
    rejs_added = max(0, rejs_now - old_total_rejs)
    ints_added = max(0, ints_now - old_total_ints)
    oas_added = max(0, oas_now - old_total_oas)

    total_process = max(old_total_process, old_total_process + total_added)
    total_companies = max(old_total_companies, len(base["companies"]))

    base["generated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    base["stats"] = {
        "total_process_msgs": total_process,
        "total_companies_tracked": total_companies,
        "total_offers": max(old_total_offers, old_total_offers + offers_added),
        "total_rejections": max(old_total_rejs, old_total_rejs + rejs_added),
        "total_interviews": max(old_total_ints, old_total_ints + ints_added),
        "total_oas": max(old_total_oas, old_total_oas + oas_added),
    }

    OUT_PATH.write_text(json.dumps(base, indent=2))
    print(f"Merged {added} new !process messages into {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
