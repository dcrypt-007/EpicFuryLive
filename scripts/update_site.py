#!/usr/bin/env python3
"""
Epic Fury Live — Automated Site Updater
Runs hourly via GitHub Actions to pull fresh conflict data and update the dashboard.

Data sources:
- RSS feeds from Al Jazeera, Reuters, BBC, CNN, AP
- Structured data extraction
- Timestamp and stats refresh

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


def update_latest_developments(html, news_items):
    """Replace the Latest Developments section with fresh news items."""
    if not news_items:
        print("  No new items to inject — keeping existing developments")
        return html

    # Build new development entries
    entries = []
    for item in news_items[:10]:
        # Try to parse the pubDate
        try:
            # RFC 822 format from RSS
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(item["pubDate"])
        except:
            dt = datetime.now(timezone.utc)

        iso = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        display = dt.strftime("%b %d, %H:%M UTC")

        title = escape(item["title"])
        desc = escape(item["description"][:200])
        source = escape(item["source"])

        entry = f"""                <div class="development-item">
                    <time class="development-time" datetime="{iso}">{display}</time>
                    <span class="development-text"><strong>{title}</strong> — {desc} <span style="color:#64748b;font-size:11px;">[{source}]</span></span>
                </div>"""
        entries.append(entry)

    new_section = "\n".join(entries)

    # Replace existing development items
    pattern = r'(<div class="latest-title">Latest Developments</div>\n)(.*?)(\n\s*</div>\s*\n\s*</div>\s*\n\s*<!-- TAB 2)'
    replacement = rf'\g<1>{new_section}\n\g<3>'

    updated = re.sub(pattern, replacement, html, flags=re.DOTALL)

    if updated == html:
        print("  Warning: Could not locate Latest Developments section to update")
    else:
        print(f"  Injected {len(entries)} development items")

    return updated


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
        link = escape(item.get("link", "https://epicfurylive.com"))
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
    <link>https://epicfurylive.com</link>
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


def update_sitemap():
    """Update sitemap.xml lastmod dates."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  <url>
    <loc>https://epicfurylive.com/</loc>
    <lastmod>{now}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://epicfurylive.com/methodology.html</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://epicfurylive.com/glossary.html</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://epicfurylive.com/rss.xml</loc>
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
    print("\n[1/5] Fetching news from RSS feeds...")
    news_items = fetch_all_feeds()
    print(f"  Total: {len(news_items)} relevant items")

    # 2. Read current HTML
    print("\n[2/5] Reading index.html...")
    with open("index.html", "r") as f:
        html = f.read()
    print(f"  Read {len(html)} bytes")

    # 3. Update timestamps
    print("\n[3/5] Updating timestamps and freshness signals...")
    html = update_timestamps(html)

    # 4. Update latest developments (only if we got fresh items)
    print("\n[4/5] Updating Latest Developments...")
    html = update_latest_developments(html, news_items)

    # 5. Write updated files
    print("\n[5/5] Writing updated files...")
    with open("index.html", "w") as f:
        f.write(html)
    print("  Wrote index.html")

    # Also sync to public/dashboard.html
    with open("public/dashboard.html", "w") as f:
        f.write(html)
    print("  Wrote public/dashboard.html")

    # Update RSS feed
    update_rss_feed(news_items)

    # Update sitemap
    update_sitemap()

    print("\n" + "=" * 60)
    print("Update complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
