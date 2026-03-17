#!/usr/bin/env python3
"""
Process 2026 summer intern Discord channel CSV exports into structured JSON.
Run: python scripts/process_data.py
"""
import csv
import glob
import json
import os
import re
from collections import defaultdict, Counter
from datetime import datetime

DATA_DIR = "/Users/akhil/Downloads/2026_summer_intern_process_kkPqaPF_Pf"
OUT_DIR = os.path.join(os.path.dirname(__file__), "../public/data")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Company keyword map ──────────────────────────────────────────────────────
COMPANIES = {
    "amazon":       ["amazon", " zon ", "zon "],
    "google":       ["google"],
    "microsoft":    ["microsoft", "msft"],
    "meta":         ["meta ", " meta,", "facebook"],
    "apple":        ["apple"],
    "openai":       ["openai", "open ai"],
    "nvidia":       ["nvidia"],
    "ibm":          ["ibm"],
    "visa":         ["visa "],
    "citadel":      ["citadel"],
    "tesla":        ["tesla"],
    "stripe":       ["stripe"],
    "capital one":  ["c1 ", "capital one", "cap1"],
    "ramp":         ["ramp "],
    "coinbase":     ["coinbase"],
    "oracle":       ["oracle"],
    "snapchat":     ["snap ", "snapchat"],
    "shopify":      ["shopify"],
    "tiktok":       ["tiktok", "tik tok", "bytedance"],
    "palantir":     ["palantir"],
    "jane street":  ["jane street"],
    "optiver":      ["optiver"],
    "two sigma":    ["two sigma"],
    "akuna":        ["akuna"],
    "bridgewater":  ["bridgewater"],
    "intuit":       ["intuit"],
    "dropbox":      ["dropbox"],
    "snowflake":    ["snowflake"],
    "uber":         ["uber "],
    "airbnb":       ["airbnb"],
    "lyft":         ["lyft"],
    "linkedin":     ["linkedin"],
    "salesforce":   ["salesforce"],
    "doordash":     ["doordash"],
    "robinhood":    ["robinhood"],
    "figma":        ["figma"],
    "cloudflare":   ["cloudflare"],
    "scale ai":     ["scale ai", "scaleai"],
    "riot games":   ["riot "],
    "xai":          ["xai", "x.ai"],
    "modal labs":   ["modal labs", "modal "],
    "anthropic":    ["anthropic"],
    "los alamos":   ["los alamos", "lanl"],
}

# ── Stage detection ──────────────────────────────────────────────────────────
STAGE_PATTERNS = {
    "offer":      ["offer", "accepted", "signed offer", "verbal offer", "got the offer", "got an offer"],
    "rejection":  ["reject", " rej ", "rej'd", "denied", "no offer", "ghosted", "got rejected", "rescind", "rescinded"],
    "interview":  ["interview", "round 1", "round 2", "r1", "r2", "behavioral", "technical", "phone screen", "virtual onsite", "onsite", "hiring manager", "hm call", "final round"],
    "oa":         ["oa ", "online assessment", "hackerrank", "codility", "codesignal", "coding assessment", "take home"],
}

def detect_stage(content: str) -> str:
    c = content.lower()
    for stage, keywords in STAGE_PATTERNS.items():
        if any(k in c for k in keywords):
            return stage
    return "question"

def match_company(content: str) -> str | None:
    c = " " + content.lower() + " "
    for company, keywords in COMPANIES.items():
        if any(k in c for k in keywords):
            return company
    return None

def parse_date(d: str) -> str:
    return d[:10] if d else ""

# ── Load all main channel pages ──────────────────────────────────────────────
print("Loading main channel data...")
all_msgs = []
for f in sorted(glob.glob(os.path.join(DATA_DIR, "2026_summer_intern_process_page_*.csv"))):
    with open(f, encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        all_msgs.extend(list(reader))

print(f"  Total messages: {len(all_msgs)}")
process_msgs = [r for r in all_msgs if r.get("content", "").lower().startswith("!process")]
print(f"  !process messages: {len(process_msgs)}")

# ── Load thread files ────────────────────────────────────────────────────────
print("Loading thread data...")
threads_raw = {}
for f in sorted(glob.glob(os.path.join(DATA_DIR, "!process*.csv"))):
    name = os.path.basename(f).replace("_page_1.csv", "")
    with open(f, encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        rows = list(reader)
    threads_raw[name] = rows

print(f"  Thread files: {len(threads_raw)}")

# ── Build company data ───────────────────────────────────────────────────────
company_data: dict[str, dict] = defaultdict(lambda: {
    "name": "",
    "count": 0,
    "stages": {"offer": 0, "rejection": 0, "interview": 0, "oa": 0, "question": 0},
    "messages": [],
    "daily": defaultdict(int),
})

for r in process_msgs:
    content = r.get("content", "")
    co = match_company(content)
    if not co:
        continue
    stage = detect_stage(content)
    date = parse_date(r.get("date", ""))
    company_data[co]["name"] = co
    company_data[co]["count"] += 1
    company_data[co]["stages"][stage] += 1
    company_data[co]["daily"][date] += 1
    if len(company_data[co]["messages"]) < 30:
        company_data[co]["messages"].append({
            "content": content[:280],
            "date": date,
            "author": r.get("author.global_name", "") or r.get("author.username", ""),
            "stage": stage,
        })

# Attach thread conversations
for thread_name, rows in threads_raw.items():
    co = match_company(thread_name)
    if not co or co not in company_data:
        continue
    convo = []
    for r in rows:
        c = r.get("content", "")
        if c:
            convo.append({
                "content": c[:400],
                "date": parse_date(r.get("date", "")),
                "author": r.get("author.global_name", "") or r.get("author.username", ""),
            })
    if convo and "threads" not in company_data[co]:
        company_data[co]["threads"] = []
    if convo:
        company_data[co].setdefault("threads", []).append({
            "title": thread_name.replace("!process ", ""),
            "messages": convo,
        })

# Finalize – convert defaultdict daily to sorted list
companies_list = []
for co, data in company_data.items():
    daily_list = sorted(
        [{"date": d, "count": c} for d, c in data["daily"].items()],
        key=lambda x: x["date"]
    )
    companies_list.append({
        "name": co,
        "count": data["count"],
        "stages": data["stages"],
        "messages": data["messages"],
        "threads": data.get("threads", []),
        "daily": daily_list,
    })

companies_list.sort(key=lambda x: -x["count"])

# ── Build timeline (all companies combined) ──────────────────────────────────
daily_all: dict[str, Counter] = defaultdict(Counter)
for r in process_msgs:
    date = parse_date(r.get("date", ""))
    if not date:
        continue
    stage = detect_stage(r.get("content", ""))
    daily_all[date][stage] += 1

timeline = sorted(
    [{"date": d, **dict(counts)} for d, counts in daily_all.items()],
    key=lambda x: x["date"]
)

# ── Recent activity ──────────────────────────────────────────────────────────
recent = []
for r in process_msgs[:50]:
    content = r.get("content", "")
    co = match_company(content)
    recent.append({
        "content": content[:200],
        "company": co,
        "stage": detect_stage(content),
        "date": parse_date(r.get("date", "")),
        "author": r.get("author.global_name", "") or r.get("author.username", ""),
    })

# ── Stats ────────────────────────────────────────────────────────────────────
total_process = len(process_msgs)
total_offers = sum(r["stages"]["offer"] for r in companies_list)
total_rejections = sum(r["stages"]["rejection"] for r in companies_list)
total_interviews = sum(r["stages"]["interview"] for r in companies_list)
total_oa = sum(r["stages"]["oa"] for r in companies_list)

# ── Write output ─────────────────────────────────────────────────────────────
output = {
    "generated": datetime.utcnow().isoformat() + "Z",
    "stats": {
        "total_process_msgs": total_process,
        "total_companies_tracked": len(companies_list),
        "total_offers": total_offers,
        "total_rejections": total_rejections,
        "total_interviews": total_interviews,
        "total_oas": total_oa,
    },
    "companies": companies_list,
    "timeline": timeline,
    "recent": recent,
}

out_path = os.path.join(OUT_DIR, "intern_data.json")
with open(out_path, "w", encoding="utf-8") as fp:
    json.dump(output, fp, indent=2)

print(f"\nDone! Written to {out_path}")
print(f"  Companies: {len(companies_list)}")
print(f"  Timeline points: {len(timeline)}")
print(f"  Stats: {output['stats']}")
