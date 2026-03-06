#!/usr/bin/env python3
"""
Epic Fury Live — Automated Site Updater + OpenClaw Cost Tracker
Runs hourly via GitHub Actions to pull fresh conflict data and update the dashboard.

OpenClaw scans RSS articles for cost-driving data (munition counts, carrier
deployments, sortie numbers, troop figures) and recalculates the financial
cost model automatically. Time-based costs (carriers at sea, personnel
deployed) accumulate daily. Event-based costs (missiles fired, sorties flown)
update when new quantities are found in reporting.

Data sources:
- RSS feeds from Al Jazeera, Reuters, BBC, CNN, AP
- Structured data extraction via OpenClaw pattern matching
- Timestamp and stats refresh
- Historical data tracking for trends

Usage:
    python3 scripts/update_site.py
"""

import re
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from html import escape
from email.utils import parsedate_to_datetime
import math

# ============================================================
# CONFIG: RSS feeds to pull from
# ============================================================
RSS_FEEDS = [
    {
        "name": "Al Jazeera - Iran",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "keywords": ["iran", "tehran", "irgc", "epic fury", "hezbollah", "strait of hormuz", "houthi"],
        "tier": 2
    },
    {
        "name": "Reuters - World",
        "url": "https://feeds.reuters.com/Reuters/worldNews",
        "keywords": ["iran", "tehran", "israel", "strike", "hezbollah", "houthi", "persian gulf"],
        "tier": 2
    },
    {
        "name": "BBC - World",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "keywords": ["iran", "israel", "us strike", "hezbollah", "houthi", "middle east"],
        "tier": 2
    },
]

# ============================================================
# FETCH RSS AND FILTER FOR CONFLICT NEWS
# ============================================================
def fetch_rss(feed_config):
    """Fetch and parse an RSS feed, filter for conflict-relevant items."""
    items = []
    try:
        req = urllib.request.Request(
            feed_config["url"],
            headers={"User-Agent": "EpicFuryLive/1.0 (conflict-tracker)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

        root = ET.fromstring(data)

        # Handle both RSS 2.0 and Atom feeds
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        rss_items = root.findall(".//item") or root.findall(".//atom:entry", ns)

        for item in rss_items[:50]:  # Check last 50 items
            title = ""
            description = ""
            pub_date = ""
            link = ""

            # RSS 2.0
            if item.find("title") is not None:
                title = item.find("title").text or ""
            if item.find("description") is not None:
                description = item.find("description").text or ""
            if item.find("pubDate") is not None:
                pub_date = item.find("pubDate").text or ""
            if item.find("link") is not None:
                link = item.find("link").text or ""

            # Atom
            if not title and item.find("atom:title", ns) is not None:
                title = item.find("atom:title", ns).text or ""

            # Check if relevant to conflict
            text = (title + " " + description).lower()
            if any(kw in text for kw in feed_config["keywords"]):
                items.append({
                    "title": title.strip(),
                    "description": re.sub(r'<[^>]+>', '', description).strip()[:300],
                    "pubDate": pub_date.strip(),
                    "link": link.strip(),
                    "source": feed_config["name"],
                    "tier": feed_config["tier"]
                })

    except Exception as e:
        print(f"  Warning: Failed to fetch {feed_config['name']}: {e}")

    return items


def fetch_all_feeds():
    """Fetch all configured RSS feeds and return combined items."""
    all_items = []
    for feed in RSS_FEEDS:
        print(f"  Fetching: {feed['name']}...")
        items = fetch_rss(feed)
        print(f"    Found {len(items)} relevant items")
        all_items.extend(items)

    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for item in all_items:
        title_key = item["title"].lower()[:50]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(item)

    return unique[:15]  # Top 15 most recent


# ============================================================
# OPENCLAW — Cost-Driving Data Extractor
# ============================================================

def extract_number_near_keyword(text, keywords, min_val=1, max_val=999999):
    """
    Search text for a number appearing near one of the keywords.
    Returns the largest number found near any keyword, or None if no match.

    Handles formats like:
    - "500 Tomahawk missiles"
    - "launched 500+ Tomahawk"
    - "more than 3,700 strikes"
    - "approximately 2,000 sorties"
    - "4 carrier strike groups"
    - "45,000 troops deployed"

    Also handles vague quantity words and converts them to estimates:
    - "dozens of" → 50
    - "hundreds of" → 500
    - "scores of" → 40
    - "several" → 5
    - "a handful of" → 5
    - "multiple" → 3

    Filters out false positives like:
    - "2,000-pound bombs" (bomb weight, not count)
    - "$14.9 billion" (dollar amounts)
    - "90 percent" (percentages)
    """
    if not keywords:
        return None

    # Vague quantity words → estimated numeric values
    VAGUE_QUANTITIES = {
        r'dozens?\s+of': 50,
        r'scores?\s+of': 40,
        r'hundreds?\s+of': 500,
        r'a\s+handful\s+of': 5,
        r'several': 5,
        r'multiple': 3,
        r'a\s+few': 3,
        r'numerous': 50,
        r'a\s+number\s+of': 20,
    }

    # Patterns that indicate a number is NOT a quantity count
    # (bomb weight, dollar amounts, percentages, dates, etc.)
    FALSE_POSITIVE_SUFFIXES = re.compile(
        r'[\-\s]*(pound|lb|kg|kilogram|ton|mile|km|kilometer|feet|foot|meter|'
        r'percent|%|billion|million|trillion|dollar|year|month|day|hour|minute|second|'
        r'inch|caliber|cal|mm|acre|fahrenheit|celsius|degree)',
        re.IGNORECASE
    )

    text_lower = text.lower()
    best_match = None

    for keyword in keywords:
        kw = keyword.lower()
        if kw not in text_lower:
            continue

        # Find all keyword positions
        kw_positions = [m.start() for m in re.finditer(re.escape(kw), text_lower)]

        for pos in kw_positions:
            # Search window around the keyword
            window_start = max(0, pos - 80)
            window_end = min(len(text), pos + len(kw) + 80)
            window = text[window_start:window_end]
            window_lower = window.lower()

            # --- PASS 1: Check for vague quantity words near the keyword ---
            # e.g., "dropped dozens of bunker busters" → 50
            for pattern, estimate in VAGUE_QUANTITIES.items():
                if re.search(pattern, window_lower):
                    if min_val <= estimate <= max_val:
                        if best_match is None or estimate > best_match:
                            best_match = estimate

            # --- PASS 2: Check for explicit numbers near the keyword ---
            # Patterns: "3,700", "500+", "~2,000", "more than 45000", "approximately 150"
            for match in re.finditer(r'(?:more than |over |approximately |about |nearly |~|>)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*\+?', window):
                num_str = match.group(1)
                # Check what comes AFTER the number — filter out false positives
                after_num = window[match.end():]
                if FALSE_POSITIVE_SUFFIXES.match(after_num):
                    continue

                try:
                    num = int(num_str.replace(',', '').split('.')[0])
                    if min_val <= num <= max_val:
                        if best_match is None or num > best_match:
                            best_match = num
                except ValueError:
                    continue

    return best_match


def openclaw_scan(news_items, cost_model):
    """
    OpenClaw engine: scan news articles for cost-driving data and update
    the cost model quantities when new, higher numbers are found.

    Returns a list of updates made.
    """
    updates = []

    if not news_items or not cost_model:
        return updates

    # Combine all article text for scanning
    all_text = ""
    for item in news_items:
        all_text += item["title"] + " " + item["description"] + " "

    if not all_text.strip():
        return updates

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Scan time-based items (look for quantity changes, e.g., more carrier groups)
    for item in cost_model.get("timeBased", []):
        if not item.get("keywords"):
            continue

        found = extract_number_near_keyword(
            all_text,
            item["keywords"],
            min_val=1,
            max_val=500000  # reasonable cap for personnel, ships, etc.
        )

        if found is not None and found > item.get("quantity", 0):
            old_qty = item["quantity"]
            item["quantity"] = found
            item["lastUpdated"] = now_str
            item["source"] = "OpenClaw (auto-detected from RSS)"
            updates.append(f"  [OpenClaw] {item['category']}: quantity {old_qty} → {found}")

    # Scan event-based items (look for higher cumulative counts)
    for item in cost_model.get("eventBased", []):
        if not item.get("keywords"):
            continue

        found = extract_number_near_keyword(
            all_text,
            item["keywords"],
            min_val=1,
            max_val=100000  # reasonable cap for munitions
        )

        if found is not None and found > item.get("quantity", 0):
            old_qty = item["quantity"]
            item["quantity"] = found
            item["lastUpdated"] = now_str
            item["source"] = "OpenClaw (auto-detected from RSS)"
            updates.append(f"  [OpenClaw] {item['category']}: quantity {old_qty} → {found}")

    return updates


def calculate_costs(cost_model, days_of_ops):
    """
    Calculate all costs from the cost model.

    Time-based items: unitCostPerDay × quantity × days active
    Event-based items: unitCost × quantity

    Returns (total_cost, daily_burn_rate, breakdown_list)
    """
    total = 0
    breakdown = []
    now = datetime.now(timezone.utc)

    # Time-based costs
    for item in cost_model.get("timeBased", []):
        qty = item.get("quantity", 0)
        cost_per_day = item.get("unitCostPerDay", 0)
        daily_cost = cost_per_day * qty
        # Calculate days active
        start = item.get("activeStartDate")
        end = item.get("activeEndDate")

        if start:
            start_dt = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if end:
                end_dt = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                active_days = (end_dt - start_dt).days
            else:
                active_days = (now - start_dt).days
            active_days = max(active_days, 1)
        else:
            active_days = days_of_ops

        line_total = daily_cost * active_days
        total += line_total

        # Format for display
        if qty > 1:
            detail = f"{qty:,} × ${cost_per_day:,.0f}/day × {active_days} days"
        else:
            detail = f"${cost_per_day:,.0f}/day × {active_days} days"

        breakdown.append({
            "category": item["category"],
            "detail": detail,
            "cost": f"${line_total:,.0f}"
        })

    # Event-based costs
    for item in cost_model.get("eventBased", []):
        qty = item.get("quantity", 0)
        unit_cost = item.get("unitCost", 0)
        line_total = unit_cost * qty
        total += line_total

        if qty > 1:
            detail = f"{qty:,} × ${unit_cost:,.0f} each"
        else:
            detail = f"Lump sum"

        breakdown.append({
            "category": item["category"],
            "detail": detail,
            "cost": f"${line_total:,.0f}"
        })

    # Daily burn = total cost / days (actual average daily spend, not just ops cost)
    days_of_ops_safe = max(days_of_ops, 1)
    daily_burn = total / days_of_ops_safe

    return total, daily_burn, breakdown


def format_cost(amount):
    """Format a dollar amount for display. E.g., 6543000000 → '$6.5 billion+'"""
    if amount >= 1_000_000_000:
        billions = amount / 1_000_000_000
        # Round to nearest 0.1 billion
        return f"${billions:,.1f} billion+"
    elif amount >= 1_000_000:
        millions = amount / 1_000_000
        return f"${millions:,.0f} million+"
    else:
        return f"${amount:,.0f}"


def format_cost_short(amount):
    """Short format for banner. E.g., 6543000000 → '$6.5B+'"""
    if amount >= 1_000_000_000:
        billions = amount / 1_000_000_000
        if billions == int(billions):
            return f"${int(billions)}B+"
        return f"${billions:.1f}B+"
    elif amount >= 1_000_000:
        millions = amount / 1_000_000
        return f"${millions:.0f}M+"
    return f"${amount:,.0f}"


# ============================================================
# UPDATE HTML FILE
# ============================================================
def update_timestamps(html):
    """Update all timestamp-related elements."""
    now = datetime.now(timezone.utc)
    iso_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    display_now = now.strftime("%b %d, %Y %H:%M UTC")

    # Update the siteLastUpdated element
    html = re.sub(
        r'<time id="siteLastUpdated"[^>]*>[^<]*</time>',
        f'<time id="siteLastUpdated" datetime="{iso_now}">{display_now}</time>',
        html
    )

    # Update the banner "Last updated" span
    html = re.sub(
        r'Last updated <span id="lastUpdated">[^<]*</span>',
        f'Last updated <span id="lastUpdated">{display_now}</span>',
        html
    )

    # Update LiveBlogPosting dateModified in JSON-LD
    html = re.sub(
        r'"dateModified":\s*"[^"]*"',
        f'"dateModified": "{iso_now}"',
        html
    )

    # Update conflict day counter start reference (Feb 28, 2026)
    start = datetime(2026, 2, 28, tzinfo=timezone.utc)
    days = (now - start).days
    html = re.sub(
        r'DAY \d+ — OPERATION EPIC FURY',
        f'DAY {days} — OPERATION EPIC FURY',
        html
    )

    return html


def update_rss_feed(news_items):
    """Regenerate rss.xml with fresh items."""
    if not news_items:
        return

    now = datetime.now(timezone.utc)
    rfc822 = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    items_xml = []
    for item in news_items[:10]:
        title = escape(item["title"])
        desc = escape(item["description"][:300])
        link = escape(item.get("link", "https://www.epicfurylive.com"))
        guid = f"epic-fury-{now.strftime('%Y%m%d')}-{hash(title) % 100000}"

        items_xml.append(f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{desc}</description>
      <pubDate>{item.get('pubDate', rfc822)}</pubDate>
      <guid>{guid}</guid>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Epic Fury Live — US-Iran War Tracker</title>
    <link>https://www.epicfurylive.com</link>
    <description>Live tracking of the US-Israel-Iran conflict. Real-time updates, verified casualties, evidence, and analysis.</description>
    <language>en-us</language>
    <lastBuildDate>{rfc822}</lastBuildDate>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""

    with open("rss.xml", "w") as f:
        f.write(rss)
    print(f"  Updated rss.xml with {len(items_xml)} items")


# ============================================================
# UPDATE DATA.JSON — All dynamic content + OpenClaw cost model
# ============================================================
def update_data_json(news_items):
    """Update data.json with current timestamps, computed values, OpenClaw cost model, and fresh RSS developments."""
    now = datetime.now(timezone.utc)
    iso_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Conflict start date
    start = datetime(2026, 2, 28, tzinfo=timezone.utc)
    days = (now - start).days

    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("  Warning: data.json not found or invalid, skipping")
        return

    # ---- TIMESTAMPS & DAY COUNT ----
    data["lastUpdated"] = iso_now
    data["dayCount"] = days

    # ---- OPENCLAW: Scan RSS for cost-driving data ----
    cost_model = data.get("financialCost", {}).get("costModel")
    if cost_model:
        print("  [OpenClaw] Scanning articles for cost-driving data...")
        updates = openclaw_scan(news_items, cost_model)
        if updates:
            for u in updates:
                print(u)
            print(f"  [OpenClaw] Made {len(updates)} quantity updates")
        else:
            print("  [OpenClaw] No new quantity updates found in articles")

        # ---- CALCULATE COSTS from model ----
        total_cost, daily_burn, breakdown = calculate_costs(cost_model, days)

        data["financialCost"]["daysOfOps"] = days
        data["financialCost"]["totalCost"] = format_cost(total_cost)
        data["financialCost"]["dailyBurnRate"] = f"~{format_cost_short(daily_burn).replace('+', '')}/day"
        data["financialCost"]["breakdown"] = breakdown

        # Update banner cost
        if "banner" in data:
            data["banner"]["cost"] = format_cost_short(total_cost)

        print(f"  [OpenClaw] Total cost: {format_cost(total_cost)} | Daily burn: {format_cost_short(daily_burn)}/day")
    else:
        # Fallback: simple formula if no cost model
        if "financialCost" in data:
            data["financialCost"]["daysOfOps"] = days
            total_billions = days
            data["financialCost"]["totalCost"] = f"${total_billions},000,000,000+"
        if "banner" in data:
            data["banner"]["cost"] = f"${days}B+"

    # ---- DEVELOPMENTS (inject RSS items) ----
    if news_items:
        new_devs = []
        for item in news_items[:10]:
            try:
                dt = parsedate_to_datetime(item["pubDate"])
            except Exception:
                dt = now

            iso_time = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            title = item["title"]
            desc = item["description"][:200]
            source = item["source"]

            new_devs.append({
                "time": iso_time,
                "text": f"<strong>{escape(title)}</strong> — {escape(desc)} <span style=\"color:#64748b;font-size:11px;\">[{escape(source)}]</span>"
            })

        if new_devs:
            existing_devs = data.get("developments", [])
            new_times = {d["time"] for d in new_devs}
            kept_existing = [d for d in existing_devs if d["time"] not in new_times]
            all_devs = new_devs + kept_existing
            data["developments"] = all_devs[:20]
            print(f"  Injected {len(new_devs)} RSS items into developments (total: {len(data['developments'])})")
    else:
        print("  No new RSS items — keeping existing developments")

    # ---- WRITE DATA.JSON ----
    # Use ensure_ascii=True so all non-ASCII chars become \uXXXX escapes.
    # This prevents encoding issues across GitHub Actions, GitHub Pages,
    # and different browser environments. The browser's JSON parser handles
    # \uXXXX escapes correctly and renders the proper Unicode characters.
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
    print(f"  Updated data.json (Day {days})")

    return data  # Return for history tracking


# ============================================================
# HISTORY TRACKING — Append daily snapshot for trend charts
# ============================================================
def update_history(data):
    """Append a snapshot of key stats to history.json for trend tracking."""
    if not data:
        return

    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    hour = now.strftime("%H:00")

    # Load existing history
    try:
        with open("history.json", "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = {"snapshots": [], "dailySummaries": []}

    # Extract key metrics for this snapshot
    snapshot = {
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "date": today,
        "hour": hour,
        "dayCount": data.get("dayCount", 0),
        "iranDeaths": data.get("humanCost", {}).get("iranDeaths", "0"),
        "usKIA": data.get("humanCost", {}).get("usKIA", "0"),
        "israeliDeaths": data.get("humanCost", {}).get("israeliDeaths", "0"),
        "gulfCasualties": data.get("humanCost", {}).get("gulfCasualties", "0"),
        "iranWounded": data.get("humanCost", {}).get("iranWounded", "0"),
        "civilianDeaths": data.get("humanCost", {}).get("civilianDeaths", "0"),
        "totalCost": data.get("financialCost", {}).get("totalCost", "$0"),
        "dailyBurnRate": data.get("financialCost", {}).get("dailyBurnRate", "$0"),
        "totalStrikes": data.get("banner", {}).get("strikes", "0"),
        "threatCount": len(data.get("threats", [])),
        "homelandThreatCount": len(data.get("homelandThreats", [])),
        "developmentCount": len(data.get("developments", []))
    }

    # Check if we already have a snapshot for this hour
    existing_hours = {s.get("timestamp", "")[:13] for s in history.get("snapshots", [])}
    current_hour_key = snapshot["timestamp"][:13]

    if current_hour_key in existing_hours:
        for i, s in enumerate(history["snapshots"]):
            if s.get("timestamp", "")[:13] == current_hour_key:
                history["snapshots"][i] = snapshot
                break
        print(f"  Updated existing history snapshot for {today} {hour}")
    else:
        history.setdefault("snapshots", []).append(snapshot)
        print(f"  Added new history snapshot for {today} {hour}")

    # Keep last 90 days of hourly data
    max_snapshots = 2160
    if len(history["snapshots"]) > max_snapshots:
        history["snapshots"] = history["snapshots"][-max_snapshots:]

    # Daily summary
    if "dailySummaries" not in history:
        history["dailySummaries"] = []

    existing_dates = {s.get("date", "") for s in history["dailySummaries"]}
    daily_data = {
        "date": today,
        "dayCount": snapshot["dayCount"],
        "iranDeaths": snapshot["iranDeaths"],
        "usKIA": snapshot["usKIA"],
        "israeliDeaths": snapshot["israeliDeaths"],
        "gulfCasualties": snapshot["gulfCasualties"],
        "civilianDeaths": snapshot["civilianDeaths"],
        "totalCost": snapshot["totalCost"],
        "dailyBurnRate": snapshot["dailyBurnRate"],
        "totalStrikes": snapshot["totalStrikes"],
        "threatCount": snapshot["threatCount"]
    }

    if today not in existing_dates:
        history["dailySummaries"].append(daily_data)
        print(f"  Added daily summary for {today}")
    else:
        for i, s in enumerate(history["dailySummaries"]):
            if s.get("date") == today:
                history["dailySummaries"][i] = daily_data
                break

    # Keep last 365 days
    if len(history["dailySummaries"]) > 365:
        history["dailySummaries"] = history["dailySummaries"][-365:]

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=True)
    print(f"  History: {len(history['snapshots'])} hourly, {len(history['dailySummaries'])} daily")


def update_sitemap():
    """Update sitemap.xml lastmod dates."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  <url>
    <loc>https://www.epicfurylive.com/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.epicfurylive.com/methodology.html</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://www.epicfurylive.com/glossary.html</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://www.epicfurylive.com/rss.xml</loc>
    <lastmod>{now}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>
"""

    with open("sitemap.xml", "w") as f:
        f.write(sitemap)
    print(f"  Updated sitemap.xml with lastmod={now}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("Epic Fury Live — Automated Update + OpenClaw")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    # 1. Fetch news
    print("\n[1/7] Fetching news from RSS feeds...")
    news_items = fetch_all_feeds()
    print(f"  Total: {len(news_items)} relevant items")

    # 2. Read current HTML
    print("\n[2/7] Reading index.html...")
    with open("index.html", "r") as f:
        html = f.read()
    print(f"  Read {len(html)} bytes")

    # 3. Update timestamps in HTML
    print("\n[3/7] Updating timestamps and freshness signals...")
    html = update_timestamps(html)

    # 4. Write updated HTML files
    print("\n[4/7] Writing updated HTML files...")
    with open("index.html", "w") as f:
        f.write(html)
    print("  Wrote index.html")
    with open("public/dashboard.html", "w") as f:
        f.write(html)
    print("  Wrote public/dashboard.html")

    # 5. Update data.json (all dynamic content + OpenClaw cost model)
    print("\n[5/7] Updating data.json + OpenClaw cost analysis...")
    data = update_data_json(news_items)

    # 6. Update history.json (trend tracking)
    print("\n[6/7] Updating history.json...")
    update_history(data)

    # 7. Update supporting files
    print("\n[7/7] Updating RSS feed and sitemap...")
    update_rss_feed(news_items)
    update_sitemap()

    print("\n" + "=" * 60)
    print("Update complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
