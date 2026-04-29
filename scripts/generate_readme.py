#!/usr/bin/env python3
"""
Generate README.md from 2026 intern process Discord CSV data.
Run: python scripts/generate_readme.py
"""
import csv, glob, re, os
from collections import defaultdict, Counter
from datetime import datetime, timezone

DATA_DIR = os.environ.get("DATA_DIR", "/Users/akhil/Downloads/cscareers.dev (1)/2026_summer_intern_process_zVWoAS6C56")
OUT_PATH = os.path.join(os.path.dirname(__file__), "../README.md")

COMPANIES = {
    # FAANG / Big Tech
    "Amazon":         ["amazon", " zon ", "zon "],
    "Google":         ["google", "goog "],
    "Microsoft":      ["microsoft", "msft"],
    "Meta":           ["meta ", " meta,", "facebook"],
    "Apple":          ["apple"],
    "Netflix":        ["netflix"],
    "OpenAI":         ["openai", "open ai", " oai "],
    "xAI":            [" xai "],
    "Anthropic":      ["anthropic"],
    # Finance / Quant
    "Citadel":        ["citadel"],
    "Jane Street":    ["jane street"],
    "Optiver":        ["optiver"],
    "Two Sigma":      ["two sigma", " 2sig ", "2sigma"],
    "HRT":            [" hrt "],
    "DRW":            [" drw "],
    "IMC":            [" imc "],
    "Virtu":          ["virtu "],
    "Akuna":          ["akuna"],
    "Bridgewater":    ["bridgewater"],
    "SIG":            [" sig "],
    "Cit Sec":        ["citsec", "cit sec"],
    "Goldman Sachs":  ["goldman", "goldman sachs"],
    "Wells Fargo":    ["wells fargo", "wells "],
    # Silicon Valley / SaaS
    "Nvidia":         ["nvidia"],
    "AMD":            [" amd "],
    "Intel":          ["intel "],
    "Qualcomm":       ["qualcomm"],
    "Salesforce":     ["salesforce"],
    "Snowflake":      ["snowflake"],
    "Stripe":         ["stripe"],
    "Ramp":           ["ramp "],
    "Coinbase":       ["coinbase"],
    "Cloudflare":     ["cloudflare"],
    "Dropbox":        ["dropbox"],
    "LinkedIn":       ["linkedin"],
    "Airbnb":         ["airbnb"],
    "Uber":           ["uber "],
    "Lyft":           ["lyft "],
    "Doordash":       ["doordash"],
    "Instacart":      ["instacart"],
    "Pinterest":      ["pinterest"],
    "Reddit":         ["reddit "],
    "Roblox":         ["roblox"],
    "Shopify":        ["shopify"],
    "Intuit":         ["intuit"],
    "Oracle":         ["oracle"],
    "IBM":            ["ibm"],
    "Visa":           ["visa "],
    "Capital One":    [" c1 ", "capital one", "cap1"],
    "Palantir":       ["palantir"],
    "Scale AI":       ["scale ai", "scaleai"],
    "TikTok":         ["tiktok", "tik tok", "bytedance"],
    "Snapchat":       ["snap ", "snapchat"],
    "Ebay":           ["ebay"],
    "PayPal":         ["paypal"],
    "HubSpot":        ["hubspot"],
    "Okta":           ["okta "],
    "MongoDB":        ["mongodb"],
    "GitHub":         ["github "],
    "Klaviyo":        ["klaviyo"],
    "Rippling":       ["rippling"],
    "Box":            [" box "],
    "Patreon":        ["patreon"],
    "Robinhood":      ["robinhood"],
    "SoFi":           ["sofi "],
    "Handshake":      ["handshake"],
    "Harvey":         ["harvey "],
    # Tesla / SpaceX / Hardware
    "Tesla":          ["tesla"],
    "SpaceX":         ["spacex"],
    "Rivian":         ["rivian"],
    "Zoox":           ["zoox"],
    "Neuralink":      ["neuralink"],
    "Sierra Space":   ["sierra space", "sierra "],
    "Aurora":         ["aurora "],
    "Nuro":           ["nuro "],
    "ARM":            [" arm "],
    "ASML":           ["asml"],
    "Ericsson":       ["ericsson"],
    "Nokia":          ["nokia"],
    # Media / Gaming / Other
    "Disney":         ["disney"],
    "Netflix":        ["netflix"],
    "Riot Games":     ["riot "],
    "Expedia":        ["expedia"],
    "Walmart":        ["walmart"],
    "CVS":            [" cvs "],
    "AT&T":           ["at&t"],
    "Cisco":          ["cisco "],
    "Docusign":       ["docusign"],
    "Geico":          ["geico"],
    "Crowdstrike":    ["crowdstrike"],
    "CrowdStrike":    ["crowdstrike"],
    "Pure Storage":   ["pure storage", "pure "],
    "Palo Alto":      ["palo alto", "palo "],
    "ZipRecruiter":   ["ziprecruiter"],
    "MathWorks":      ["mathworks"],
    # Together / AI startups
    "Together AI":    ["together ai", "together "],
    "Gemini":         ["gemini "],
    "Salesforce":     ["salesforce"],
}

STAGE_PATTERNS = {
    "offer":      ["offer", "accepted", "verbal offer", "got the offer", "got an offer"],
    "rejection":  ["reject", " rej ", "rej'd", "denied", "no offer", "ghosted", "got rejected", "rescind"],
    "interview":  ["interview", "round 1", "round 2", " r1 ", " r2 ", "behavioral", "technical", "phone screen", "onsite", "hm call", "hiring manager"],
    "oa":         ["oa ", "online assessment", "hackerrank", "codility", "codesignal", "coding assessment", "take home"],
}

def detect_stage(content):
    c = content.lower()
    for stage, kws in STAGE_PATTERNS.items():
        if any(k in c for k in kws):
            return stage
    return "question"

def match_company(content):
    c = " " + content.lower() + " "
    for company, kws in COMPANIES.items():
        if any(k in c for k in kws):
            return company
    return None

def clean(content: str) -> str:
    """Strip Discord mentions, newlines, and stray !process lines."""
    # Remove Discord mentions like <@123456>
    content = re.sub(r'<@!?\d+>', '', content)
    # Take only first line (some messages have embedded newlines with other !process msgs)
    content = content.split('\n')[0].strip()
    # Strip leading !process prefix
    content = re.sub(r'^!process\s*', '', content, flags=re.IGNORECASE).strip()
    return content

def bar(filled, total, length=10, fill="█", empty="░"):
    if total == 0:
        return empty * length
    n = round((filled / total) * length)
    return fill * n + empty * (length - n)

def strip_emojis(s: str) -> str:
    """Remove emoji/non-ASCII except bar-chart block chars. Replace em dash with hyphen."""
    s = s.replace("\u2014", " - ").replace("\u2013", " - ")
    return "".join(ch for ch in s if ord(ch) < 128 or ch in "█░")

def clean_snippet(s: str) -> str:
    """Sanitize a user-generated snippet for a markdown table cell."""
    s = s.replace("|", "\\|").replace("`", "'")
    s = s.replace("\u2014", " - ").replace("\u2013", " - ")
    return s

# ── Load data ────────────────────────────────────────────────────────────────
all_main = []
for f in sorted(glob.glob(os.path.join(DATA_DIR, "2026_summer_intern_process_page_*.csv"))):
    with open(f, encoding="utf-8") as fp:
        all_main.extend(list(csv.DictReader(fp)))

process_msgs = [r for r in all_main if r.get("content", "").lower().startswith("!process")]

# ── Per-company aggregation ──────────────────────────────────────────────────
company_stats = defaultdict(lambda: Counter())
company_recent = defaultdict(list)  # recent offer/interview msgs

for r in process_msgs:
    content = r.get("content", "")
    co = match_company(content)
    if not co:
        continue
    stage = detect_stage(content)
    company_stats[co][stage] += 1
    company_stats[co]["total"] += 1
    if stage in ("offer", "interview", "rejection") and len(company_recent[co]) < 3:
        company_recent[co].append({
            "stage": stage,
            "content": clean(content)[:120],
            "date": r.get("date", "")[:10],
        })

# Sort by total desc
sorted_cos = sorted(company_stats.items(), key=lambda x: -x[1]["total"])

# Global stats
total_msgs = len(process_msgs)
total_offers = sum(v["offer"] for v in company_stats.values())
total_ints = sum(v["interview"] for v in company_stats.values())
total_oas = sum(v["oa"] for v in company_stats.values())
total_rejs = sum(v["rejection"] for v in company_stats.values())
num_cos = len(company_stats)

# ── Recent hot companies (most active last 14d) ───────────────────────────────
cutoff = "2026-03-01"
recent_activity = defaultdict(int)
for r in process_msgs:
    if r.get("date", "")[:10] >= cutoff:
        co = match_company(r.get("content", ""))
        if co:
            recent_activity[co] += 1

hot_cos = sorted(recent_activity.items(), key=lambda x: -x[1])[:5]

# ── Recent offers (last 14d) ─────────────────────────────────────────────────
recent_offers = []
for r in process_msgs:
    content = r.get("content", "")
    d = r.get("date", "")[:10]
    stage = detect_stage(content)
    co = match_company(content)
    if stage == "offer" and d >= cutoff and co:
        snippet = clean(content)[:90]
        recent_offers.append((d, co, snippet))

recent_offers = sorted(recent_offers, key=lambda x: x[0], reverse=True)[:10]

# ── Status board: per-company, last 14 days ──────────────────────────────────
from collections import OrderedDict

DAYS_BACK = 14
all_dates = sorted(set(r.get("date","")[:10] for r in process_msgs if r.get("date","")))
recent_dates = sorted(d for d in all_dates if d >= cutoff)[-DAYS_BACK:]

# Per-company: stage counts in last 14d, last active date, dominant recent stage
co_status: dict[str, dict] = {}
for r in process_msgs:
    d = r.get("date","")[:10]
    if d < cutoff:
        continue
    content = r.get("content","")
    co = match_company(content)
    if not co:
        continue
    stage = detect_stage(content)
    if co not in co_status:
        co_status[co] = {"offer":0,"interview":0,"oa":0,"rejection":0,"question":0,"total":0,"last":d,"daily": defaultdict(int)}
    co_status[co][stage] += 1
    co_status[co]["total"] += 1
    if d > co_status[co]["last"]:
        co_status[co]["last"] = d
    co_status[co]["daily"][d] += 1

def current_stage_label(s: dict) -> tuple[str, str]:
    """Return (emoji, label) for the dominant *actionable* stage."""
    if s["offer"] >= 2:
        return "🎉", "Offers Rolling"
    if s["offer"] == 1 and s["interview"] == 0 and s["oa"] == 0:
        return "🎉", "Offer Seen"
    if s["interview"] >= s["oa"] and s["interview"] > 0:
        return "🎙️", "Interviewing"
    if s["oa"] > s["interview"] and s["oa"] > 0:
        return "📝", "OA Wave"
    if s["rejection"] > s["offer"] and s["rejection"] > 0:
        return "💀", "Rejections Out"
    if s["total"] > 0:
        return "💬", "Active"
    return "⚫", "Quiet"

def activity_dot(count: int) -> str:
    if count == 0: return "⬜"
    if count <= 2: return "🟦"
    if count <= 5: return "🟩"
    if count <= 10: return "🟨"
    return "🟥"

# Group active companies into status buckets
buckets: dict[str, list] = {"🎉 Offers Rolling": [], "🎙️ Interviewing": [], "📝 OA Wave": [], "💀 Rejections Out": [], "💬 Active": []}
for co, s in sorted(co_status.items(), key=lambda x: -x[1]["total"]):
    _, label = current_stage_label(s)
    key = f"🎉 Offers Rolling" if "Offer" in label else \
          f"🎙️ Interviewing" if "Interview" in label else \
          f"📝 OA Wave" if "OA" in label else \
          f"💀 Rejections Out" if "Rejection" in label else "💬 Active"
    buckets[key].append((co, s))

# Daily OA + offer heatmap across all companies (last 14d)
daily_oa: dict[str, int] = defaultdict(int)
daily_offer: dict[str, int] = defaultdict(int)
daily_int: dict[str, int] = defaultdict(int)
for r in process_msgs:
    d = r.get("date","")[:10]
    if d < cutoff:
        continue
    stage = detect_stage(r.get("content",""))
    if stage == "oa": daily_oa[d] += 1
    elif stage == "offer": daily_offer[d] += 1
    elif stage == "interview": daily_int[d] += 1

# ── Generate README ──────────────────────────────────────────────────────────
now = datetime.now(timezone.utc).strftime("%b %d, %Y %H:%M UTC")
IS_URL = "https://interviewsense.org"
IS_DASH = "https://interviewsense.org/dashboard"
PREP_BADGE = "https://img.shields.io/badge/Prep-4F5BD5?style=flat-square&logoColor=white"

def prep_link(co: str) -> str:
    slug = co.lower().replace(" ", "-").replace("&", "and")
    return f"[![Prep]({PREP_BADGE})]({IS_DASH}?company={slug})"

# Per-bucket report counts (last 14d)
bucket_co_counts = {k: len(v) for k, v in buckets.items()}
bucket_msg_counts = {k: sum(s["total"] for _, s in v) for k, v in buckets.items()}

lines = []

# ── Header ────────────────────────────────────────────────────────────────────
lines += [
    f"# 🧠 2026 Summer Intern Process Tracker",
    f"",
    f"We track every `!process` message in the **2026 Summer Intern Process Discord channel** and turn it into something actually useful — `{total_msgs:,}` reports, `{num_cos}` companies, scraped and rebuilt every 24 hours.",
    f"",
    f"![Updated](https://img.shields.io/badge/updated-{now.replace(' ','%20').replace(',','').replace(':','%3A')}-4F5BD5?style=flat-square) "
    f"![Reports](https://img.shields.io/badge/reports-{total_msgs:,}-4F5BD5?style=flat-square) "
    f"![Offers](https://img.shields.io/badge/offers-{total_offers}-22c55e?style=flat-square) "
    f"![Companies](https://img.shields.io/badge/companies-{num_cos}-4F5BD5?style=flat-square) "
    f"![Cadence](https://img.shields.io/badge/updates-every%2024h-4F5BD5?style=flat-square)",
    f"",
    f"---",
    f"",
]

# ── Browse by what's happening ────────────────────────────────────────────────
BUCKET_ANCHORS = {
    "Offers Rolling":  "#offers-rolling",
    "Interviewing":    "#interviewing",
    "OA Wave":         "#oa-wave",
    "Rejections Out":  "#rejections-out",
    "Active":          "#active",
}
BUCKET_EMOJI = {
    "Offers Rolling":  "🎉",
    "Interviewing":    "🎙️",
    "OA Wave":         "📝",
    "Rejections Out":  "💀",
    "Active":          "💬",
}
BUCKET_DESC = {
    "Offers Rolling":  "companies actively extending offers",
    "Interviewing":    "companies in active interview rounds",
    "OA Wave":         "companies sending online assessments",
    "Rejections Out":  "recent rejection waves",
    "Active":          "companies with recent process activity",
}

lines += [
    f"### 📡 Browse {sum(s['total'] for _, s in co_status.items() if any(True for d in [s] if d['total']>0)):,} Recent Reports by Status",
    f"",
]
for bucket_name, cos in buckets.items():
    if not cos:
        continue
    clean = re.sub(r'^[\W]+', '', bucket_name).strip()
    anchor = BUCKET_ANCHORS.get(clean, "")
    emoji = BUCKET_EMOJI.get(clean, "")
    desc = BUCKET_DESC.get(clean, "")
    n_cos = len(cos)
    n_msgs = sum(s["total"] for _, s in cos)
    lines.append(f"{emoji} **[{clean}]({anchor})** ({n_cos} companies, {n_msgs} reports) — {desc}")
    lines.append("")

lines += [
    "---",
    "",
]

# ── InterviewSense CTA ─────────────────────────────────────────────────────────
lines += [
    f"### 😤 Struggling with interviews at these companies?",
    f"",
    f"**[Get AI mock interviews built around every company in this list]({IS_URL})**",
    f"",
    f'<a href="{IS_URL}">',
    f'  <img src="assets/logo.png" alt="InterviewSense" width="90" />',
    f"</a>",
    f"",
    f"[![Start Free on InterviewSense](https://img.shields.io/badge/Start%20Free%20on%20InterviewSense-4F5BD5?style=for-the-badge&logoColor=white)]({IS_URL})",
    f"",
    f"*Stop grinding random LeetCode. InterviewSense knows which companies are sending OAs right now and builds mock interviews around their actual process: OA patterns, behavioral rounds, quant prep, system design, and more.*",
    f"",
    f"---",
    f"",
]

# ── Season at a Glance ────────────────────────────────────────────────────────
lines += [
    f"## 📊 Season at a Glance",
    f"",
    f"| Metric | Count |",
    f"|--------|-------|",
    f"| 💬 Total process reports | `{total_msgs:,}` |",
    f"| 🏢 Companies tracked | `{num_cos}` |",
    f"| 🎙️ Interviews reported | `{total_ints:,}` |",
    f"| 📝 OAs mentioned | `{total_oas:,}` |",
    f"| 🎉 Offers reported | `{total_offers:,}` |",
    f"| 💀 Rejections reported | `{total_rejs:,}` |",
    f"",
    f"---",
    f"",
]

# ── Hot Right Now ─────────────────────────────────────────────────────────────
lines += [
    f"## 🔥 Hot Right Now",
    f"",
    f"Most discussed companies since March 1:",
    f"",
]

for co, cnt in hot_cos:
    s = company_stats[co]
    tag = " — offers rolling 🎉" if s["offer"] > 0 else ""
    lines.append(f"- **{co}** — `{cnt}` recent reports{tag}")

lines += [
    "",
    "---",
    "",
]

# ── Live Status Board ─────────────────────────────────────────────────────────
lines += [
    "## 📡 Live Status Board",
    "",
    "> Synthesized from the last 14 days of process messages. Click the blue **Prep** button on any company to practice that interview on [InterviewSense](https://interviewsense.org).",
    "",
]

for bucket_name, cos in buckets.items():
    if not cos:
        continue
    clean_bucket = re.sub(r'^[\W]+', '', bucket_name).strip()
    emoji = BUCKET_EMOJI.get(clean_bucket, "")
    lines.append(f"### {emoji} {clean_bucket}")
    lines.append("")
    lines.append("| Company | 14d Reports | Offers | Interviews | OAs | Rejections | Last Active | Prep |")
    lines.append("|---------|-------------|--------|------------|-----|------------|-------------|------|")
    for co, s in cos[:12]:
        lines.append(
            f"| **{co}** | `{s['total']}` | `{s['offer']}` | `{s['interview']}` "
            f"| `{s['oa']}` | `{s['rejection']}` | `{s['last']}` | {prep_link(co)} |"
        )
    lines.append("")

lines += [
    "---",
    "",
]

# ── Recent Offers ─────────────────────────────────────────────────────────────
lines += [
    "## 🎉 Recent Offers (March 2026)",
    "",
    "| Date | Company | What they said |",
    "|------|---------|----------------|",
]
for d, co, snippet in sorted(recent_offers, key=lambda x: x[0], reverse=True):
    safe = clean_snippet(snippet)
    lines.append(f"| `{d}` | **{co}** | {safe} |")

lines += [
    "",
    "---",
    "",
]

# ── Company Leaderboard ───────────────────────────────────────────────────────
lines += [
    "## 🏆 Company Leaderboard",
    "",
    "Sorted by total all-time reports.",
    "",
    "| # | Company | Reports | Offers | Interviews | OAs | Rejections | Offer Rate | Activity |",
    "|---|---------|---------|--------|------------|-----|------------|------------|----------|",
]

for i, (co, s) in enumerate(sorted_cos, 1):
    total = s["total"]
    offer_rate = f"{(s['offer']/total*100):.0f}%" if total > 0 else "-"
    activity = bar(min(total, 500), 500, length=8)
    lines.append(
        f"| {i} | **{co}** | `{total}` | `{s['offer']}` | `{s['interview']}` | `{s['oa']}` | `{s['rejection']}` | `{offer_rate}` | `{activity}` |"
    )

lines += [
    "",
    "---",
    "",
    f"*Scraped and rebuilt every 24 hours. Last run: {now}. Source: {total_msgs:,} Discord `!process` messages.*",
]

readme = "\n".join(lines)
with open(OUT_PATH, "w", encoding="utf-8") as fp:
    fp.write(readme)

print(f"README written to {OUT_PATH}")
print(f"  {len(lines)} lines, {len(readme):,} chars")
print(f"  {num_cos} companies, {total_msgs:,} messages")
