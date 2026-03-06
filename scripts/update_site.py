#!/usr/bin/env python3
"""
Epic Fury Live — Automated Site Updater
Runs hourly via GitHub Actions to pull fresh conflict data and update the dashboard.

Data sources:
- RSS feeds from Al Jazeera, Reuters, BBC, CNN, AP
- Structured data extraction
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
# UPDATE DATA.JSON — All dynamic content
# ============================================================
def update_data_json(news_items):
    """Update data.json with current timestamps, computed values, and fresh RSS developments."""
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

    # ---- FINANCIAL COST (auto-calculated) ----
    if "financialCost" in data:
        data["financialCost"]["daysOfOps"] = days

        # Recalculate total cost based on burn rate (~$1B/day)
        total_billions = days
        data["financialCost"]["totalCost"] = f"${total_billions},000,000,000+"

        # Update carrier ops in the breakdown array
        if "breakdown" in data["financialCost"]:
            carrier_cost = 2 * 7_000_000 * days
            for item in data["financialCost"]["breakdown"]:
                if item.get("category") == "Carrier Ops":
                    item["detail"] = f"2 CSGs @ $7M/day × {days} days"
                    item["cost"] = f"${carrier_cost:,}"
                    break

    # ---- BANNER STATS ----
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
            # Merge: put new items first, keep existing items that aren't duplicates
            existing_devs = data.get("developments", [])
            new_times = {d["time"] for d in new_devs}

            # Keep existing items that don't overlap with new ones
            kept_existing = [d for d in existing_devs if d["time"] not in new_times]

            # Combine and limit to 20 most recent
            all_devs = new_devs + kept_existing
            data["developments"] = all_devs[:20]
            print(f"  Injected {len(new_devs)} RSS items into developments (total: {len(data['developments'])})")
    else:
        print("  No new RSS items — keeping existing developments")

    # ---- WRITE DATA.JSON ----
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Updated data.json (Day {days}, cost ${days}B+)")

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
        history = {"snapshots": []}

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
        "totalStrikes": data.get("banner", {}).get("strikes", "0"),
        "threatCount": len(data.get("threats", [])),
        "homelandThreatCount": len(data.get("homelandThreats", [])),
        "developmentCount": len(data.get("developments", []))
    }

    # Check if we already have a snapshot for this hour (avoid duplicates)
    existing_hours = {s.get("timestamp", "")[:13] for s in history["snapshots"]}
    current_hour_key = snapshot["timestamp"][:13]

    if current_hour_key in existing_hours:
        # Update the existing entry for this hour instead of adding a duplicate
        for i, s in enumerate(history["snapshots"]):
            if s.get("timestamp", "")[:13] == current_hour_key:
                history["snapshots"][i] = snapshot
                break
        print(f"  Updated existing history snapshot for {today} {hour}")
    else:
        history["snapshots"].append(snapshot)
        print(f"  Added new history snapshot for {today} {hour}")

    # Keep last 90 days of hourly data (90 * 24 = 2160 max snapshots)
    max_snapshots = 2160
    if len(history["snapshots"]) > max_snapshots:
        history["snapshots"] = history["snapshots"][-max_snapshots:]

    # Also maintain a daily summary for long-term trends
    if "dailySummaries" not in history:
        history["dailySummaries"] = []

    # Check if we already have a daily summary for today
    existing_dates = {s.get("date", "") for s in history["dailySummaries"]}
    if today not in existing_dates:
        history["dailySummaries"].append({
            "date": today,
            "dayCount": snapshot["dayCount"],
            "iranDeaths": snapshot["iranDeaths"],
            "usKIA": snapshot["usKIA"],
            "israeliDeaths": snapshot["israeliDeaths"],
            "gulfCasualties": snapshot["gulfCasualties"],
            "civilianDeaths": snapshot["civilianDeaths"],
            "totalCost": snapshot["totalCost"],
            "totalStrikes": snapshot["totalStrikes"],
            "threatCount": snapshot["threatCount"]
        })
        print(f"  Added daily summary for {today}")
    else:
        # Update today's daily summary with latest values
        for i, s in enumerate(history["dailySummaries"]):
            if s.get("date") == today:
                history["dailySummaries"][i].update({
                    "iranDeaths": snapshot["iranDeaths"],
                    "usKIA": snapshot["usKIA"],
                    "israeliDeaths": snapshot["israeliDeaths"],
                    "gulfCasualties": snapshot["gulfCasualties"],
                    "civilianDeaths": snapshot["civilianDeaths"],
                    "totalCost": snapshot["totalCost"],
                    "totalStrikes": snapshot["totalStrikes"],
                    "threatCount": snapshot["threatCount"]
                })
                break

    # Keep last 365 days of daily summaries
    if len(history["dailySummaries"]) > 365:
        history["dailySummaries"] = history["dailySummaries"][-365:]

    with open("history.json", "w") as f:
        json.dump(history, f, indent=2)
    print(f"  History: {len(history['snapshots'])} hourly snapshots, {len(history['dailySummaries'])} daily summaries")


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
    print("Epic Fury Live — Automated Update")
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

    # Also sync to public/dashboard.html
    with open("public/dashboard.html", "w") as f:
        f.write(html)
    print("  Wrote public/dashboard.html")

    # 5. Update data.json (all dynamic content + RSS developments)
    print("\n[5/7] Updating data.json...")
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
