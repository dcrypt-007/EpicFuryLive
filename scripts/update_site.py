#!/usr/bin/env python3
"""
Epic Fury Live — Automated Site Updater + LLM-Driven Cost Tracker
Runs hourly via GitHub Actions to pull fresh conflict data and update the dashboard.

ALL dynamic numbers (casualties, strikes, cost model quantities) are updated
by GPT-5.4 with web search. The LLM understands context and returns only
confirmed, source-backed numbers — replacing the old OpenClaw keyword scanner
which caused false positives by blindly extracting numbers near trigger words.

Time-based costs (carriers at sea, personnel deployed) accumulate daily.
Event-based costs (missiles fired, sorties flown) update when the LLM finds
new confirmed quantities from credible sources.

Data sources:
- RSS feeds from Al Jazeera, Reuters, BBC, CNN, AP, Google News
- LLM-powered stat extraction (GPT-5.4 + web search, Claude fallback)
- Timestamp and stats refresh
- Historical data tracking for trends

Usage:
    python3 scripts/update_site.py
"""

import os
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
# LLM-POWERED STAT UPDATES (Anthropic Claude API)
# ============================================================
# Instead of unreliable regex scanning of RSS articles,
# we ask an LLM to provide current, verified conflict stats.
# The LLM has access to recent news and can synthesize
# accurate figures that no pattern matcher could extract.
# ============================================================

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


LLM_STATS_PROMPT = """You are a fact-checker for epicfurylive.com, a live war tracker for the 2026 US-Israel-Iran war (Operation Epic Fury), which began February 28, 2026. Today is {today}, Day {day_count}.

IMPORTANT: Use your web search tool to look up the CURRENT CONFIRMED numbers for each field below. Search for the latest reporting from Pentagon, CENTCOM, IDF, Iran Ministry of Health, Reuters, AP, Al Jazeera, etc.

Search queries to try:
- "US soldiers killed Operation Epic Fury" or "US KIA Iran war 2026"
- "Israeli deaths Iran war 2026"
- "Iran death toll US strikes 2026"
- "Iran war casualties March 2026"
- "US military Iran deployment troops 2026"
- "Tomahawk missiles fired Iran 2026"
- "US airstrikes sorties Iran 2026"
- "carrier strike group deployed Iran 2026"
- "US drones Iran MQ-9 Reaper 2026"
- "missile interceptors Iran THAAD SM-3 2026"
- "B-2 bomber sorties Iran bunker buster 2026"

ADDITIONAL CONTEXT — today's RSS headlines:
{headlines}

CURRENT VALUES IN OUR DATABASE (for reference — update ONLY if you find newer confirmed data):
{current_values}

RULES:
- Use ONLY numbers backed by named sources you found via web search or in the headlines above.
- Do NOT estimate or guess. If you cannot find a confirmed number, return null.
- Cite the source URL or name for every non-null value.
- These are CUMULATIVE totals, not daily increments.
- For military quantities: understand context! "1,200 drone strikes" means 1,200 individual strikes, NOT 1,200 drone units deployed. Read carefully.
- A number near a keyword does NOT mean it applies to that keyword. "The US has fired 500 Tomahawks" is valid. "500 people were killed near a Tomahawk site" is NOT a Tomahawk count.

=== SECTION 1: CASUALTY FIELDS ===
- iranDeaths: Total Iranian deaths (cite which source — Iran MOH, HRANA, etc.)
- usKIA: US military killed in action — ONLY Pentagon/CENTCOM confirmed deaths
- israeliDeaths: Israeli military + civilian deaths from IDF or Israeli media
- civilianDeaths: Iranian civilian casualties from humanitarian/media sources
- iranWounded: Iranian wounded from credible sources
- gulfCasualties: Deaths in Gulf states (UAE, Saudi, Kuwait, Bahrain)
- totalStrikes: Combined US-Israeli strikes from official briefings
- bannerKilled: TOTAL killed across ALL parties (sum of confirmed figures)

=== SECTION 2: MILITARY COST MODEL — QUANTITIES DEPLOYED/USED ===
These are the quantities that drive our financial cost model. Update ONLY with confirmed numbers.

TIME-BASED (ongoing operations — how many are currently deployed/active):
- carrier_ops: Number of US carrier strike groups currently deployed to the theater (currently {carrier_ops}). Search "carrier strike group Iran" or "CSG deployed Middle East".
- destroyers: Number of US destroyers/escorts in theater (currently {destroyers}). Search "US Navy destroyers Iran" or "DDG deployed CENTCOM".
- personnel: Total US military personnel deployed for this operation (currently {personnel}). Search "US troops deployed Iran" or "CENTCOM troop levels".
- drone_ops: Number of active drone/UAV operational units (not individual strikes — this is units like MQ-9 squadrons). Currently {drone_ops}. Search "MQ-9 Reaper deployed Iran" or "US drone units Middle East".

EVENT-BASED (cumulative totals — how many have been fired/flown total):
- tomahawk: Total Tomahawk cruise missiles fired (currently {tomahawk}). Search "Tomahawk missiles fired Iran 2026".
- jdam: Total JDAM guided bombs dropped (currently {jdam}). Search "JDAM bombs dropped Iran".
- jassm: Total JASSM/JASSM-ER standoff missiles fired (currently {jassm}). Search "JASSM missiles fired Iran".
- sdb: Total Small Diameter Bombs used (currently {sdb}). Search "SDB bombs Iran".
- b2_sorties: Total B-2 stealth bomber sorties flown (currently {b2_sorties}). Search "B-2 bomber sorties Iran".
- mop_bunker_busters: Total GBU-57 MOP bunker busters dropped (currently {mop_bunker_busters}). CRITICAL: The US only has ~20 MOPs in inventory. This number should rarely exceed 20-30. Search "GBU-57 MOP Iran bunker".
- fighter_sorties: Total fighter/attack aircraft sorties flown (currently {fighter_sorties}). Search "US fighter sorties Iran" or "combat sorties CENTCOM".
- interceptors: Total missile interceptors fired — SM-3, THAAD, Patriot (currently {interceptors}). Search "missile interceptors fired Iran" or "SM-3 THAAD intercepts".

Return ONLY valid JSON, no markdown, no explanation:
{{
  "iranDeaths": {{"value": null, "note": "source"}},
  "usKIA": {{"value": null, "note": "source"}},
  "israeliDeaths": {{"value": null, "note": "source"}},
  "civilianDeaths": {{"value": null, "note": "source"}},
  "iranWounded": {{"value": null, "note": "source"}},
  "gulfCasualties": {{"value": null, "note": "source"}},
  "totalStrikes": {{"value": null, "note": "source"}},
  "bannerKilled": {{"value": null, "note": "sum of confirmed figures"}},
  "carrier_ops": {{"value": null, "note": "source"}},
  "destroyers": {{"value": null, "note": "source"}},
  "personnel": {{"value": null, "note": "source"}},
  "drone_ops": {{"value": null, "note": "source"}},
  "tomahawk": {{"value": null, "note": "source"}},
  "jdam": {{"value": null, "note": "source"}},
  "jassm": {{"value": null, "note": "source"}},
  "sdb": {{"value": null, "note": "source"}},
  "b2_sorties": {{"value": null, "note": "source"}},
  "mop_bunker_busters": {{"value": null, "note": "source"}},
  "fighter_sorties": {{"value": null, "note": "source"}},
  "interceptors": {{"value": null, "note": "source"}},
  "newThreats": [],
  "summary": "One paragraph summary of today's key developments based on confirmed reporting only"
}}"""


def llm_update_stats(days, news_items=None, current_data=None):
    """
    Call the Anthropic Claude API to extract updated stats from today's headlines.
    Feeds fresh RSS headlines to GPT and asks for confirmed, source-backed numbers.
    No current values are sent — GPT reports what sources say, not incremental updates.
    Returns a dict of updated stats, or None if the API call fails.
    """
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
        print("  [LLM] No API keys set — skipping LLM stat update")
        return None

    now = datetime.now(timezone.utc)
    today = now.strftime("%B %d, %Y")

    # Build headlines string from RSS items
    headlines = "No headlines available"
    if news_items:
        headline_lines = []
        for item in news_items[:20]:
            title = item.get("title", "")
            desc = item.get("description", "")[:200]
            source = item.get("source", "")
            headline_lines.append(f"- [{source}] {title}: {desc}")
        headlines = "\n".join(headline_lines)

    # Build current values string so the LLM knows what we have
    current_values = "No current data available"
    if current_data:
        cv_lines = []
        human = current_data.get("humanCost", {})
        banner = current_data.get("banner", {})
        cv_lines.append(f"- iranDeaths: {human.get('iranDeaths', 'unknown')}")
        cv_lines.append(f"- usKIA: {human.get('usKIA', 'unknown')}")
        cv_lines.append(f"- israeliDeaths: {human.get('israeliDeaths', 'unknown')}")
        cv_lines.append(f"- civilianDeaths: {human.get('civilianDeaths', 'unknown')}")
        cv_lines.append(f"- iranWounded: {human.get('iranWounded', 'unknown')}")
        cv_lines.append(f"- gulfCasualties: {human.get('gulfCasualties', 'unknown')}")
        cv_lines.append(f"- totalStrikes: {banner.get('strikes', 'unknown')}")
        cv_lines.append(f"- bannerKilled: {banner.get('killed', 'unknown')}")
        current_values = "\n".join(cv_lines)

    # Extract current cost model quantities for the prompt
    cost_quantities = {}
    cost_model = current_data.get("financialCost", {}).get("costModel", {}) if current_data else {}
    for item in cost_model.get("timeBased", []) + cost_model.get("eventBased", []):
        cost_quantities[item.get("id", "")] = item.get("quantity", 0)

    prompt = LLM_STATS_PROMPT.format(
        today=today,
        day_count=days,
        headlines=headlines,
        current_values=current_values,
        carrier_ops=cost_quantities.get("carrier_ops", "unknown"),
        destroyers=cost_quantities.get("destroyers", "unknown"),
        personnel=cost_quantities.get("personnel", "unknown"),
        drone_ops=cost_quantities.get("drone_ops", "unknown"),
        tomahawk=cost_quantities.get("tomahawk", "unknown"),
        jdam=cost_quantities.get("jdam", "unknown"),
        jassm=cost_quantities.get("jassm", "unknown"),
        sdb=cost_quantities.get("sdb", "unknown"),
        b2_sorties=cost_quantities.get("b2_sorties", "unknown"),
        mop_bunker_busters=cost_quantities.get("mop_bunker_busters", "unknown"),
        fighter_sorties=cost_quantities.get("fighter_sorties", "unknown"),
        interceptors=cost_quantities.get("interceptors", "unknown"),
    )

    # Try OpenAI first (GPT-5.4 — fast, cheap, cooperative), then fall back to Claude
    text = None

    if OPENAI_API_KEY:
        text = _call_openai(prompt)

    if text is None and ANTHROPIC_API_KEY:
        text = _call_anthropic(prompt)

    if text is None:
        print("  [LLM] No API key available or all API calls failed")
        return None

    # Parse JSON from the response (handle potential markdown wrapping)
    try:
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

        stats = json.loads(text)
        print("  [LLM] Successfully parsed updated stats")
        return stats

    except json.JSONDecodeError as e:
        print(f"  [LLM] Failed to parse JSON response: {e}")
        print(f"  [LLM] Raw text: {text[:500]}...")
        return None


def _call_openai(prompt):
    """Call OpenAI Responses API with web_search enabled.
    GPT can search the live internet to find real confirmed numbers."""
    request_body = json.dumps({
        "model": "gpt-5.4",
        "tools": [{"type": "web_search"}],
        "instructions": "You are a data extraction assistant. Return ONLY valid JSON. No markdown, no explanation.",
        "input": prompt
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )

    try:
        print("  [LLM] Calling OpenAI Responses API (GPT-5.4 + web search)...")
        with urllib.request.urlopen(req, timeout=60) as resp:
            response = json.loads(resp.read().decode("utf-8"))

        # Extract text from the Responses API output array
        # The output is an array of items; we need type="message" items
        text = ""
        for item in response.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text += content.get("text", "")

        if not text:
            # Fallback: try output_text top-level helper
            text = response.get("output_text", "")

        if text:
            print("  [LLM] Got response from OpenAI (with web search)")
            return text.strip()
        else:
            print(f"  [LLM] OpenAI returned empty output. Keys: {list(response.keys())}")
            return None

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"  [LLM] OpenAI API error {e.code}: {error_body[:300]}")
        return None
    except Exception as e:
        print(f"  [LLM] OpenAI failed: {e}")
        return None


def _call_anthropic(prompt):
    """Call Anthropic Claude API. Returns raw text response or None."""
    request_body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        print("  [LLM] Calling Claude API for stat extraction...")
        with urllib.request.urlopen(req, timeout=30) as resp:
            response = json.loads(resp.read().decode("utf-8"))
        text = response["content"][0]["text"].strip()
        print("  [LLM] Got response from Claude")
        return text
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"  [LLM] Claude API error {e.code}: {error_body[:200]}")
        return None
    except Exception as e:
        print(f"  [LLM] Claude failed: {e}")
        return None


# ============================================================
# AI DAILY BRIEFING — Long-form article generated once per day
# ============================================================

LLM_BRIEFING_PROMPT = """You are a senior intelligence analyst writing a daily briefing for epicfurylive.com, a live war tracker for the 2026 US-Israel-Iran conflict (Operation Epic Fury), which began February 28, 2026. Today is {today}, Day {day_count}.

Use your web search tool extensively to find the LATEST information from the past 24 hours. Search for:
- "Operation Epic Fury latest" or "US Iran war today {today}"
- "Iran war military operations today"
- "oil prices Iran conflict" or "Brent crude today"
- "Iran war market reaction" or "stock market Iran"
- "Iran war humanitarian" or "civilian casualties Iran war"
- "Iran diplomacy talks ceasefire"
- "gas hoarding Asia" or "fuel shortages Iran war"

Write a comprehensive ~1500-word intelligence briefing covering ALL of the following sections. Use ## for section headers:

## Military Operations Summary
What happened in the last 24 hours? US/Coalition strikes, Iranian responses, naval operations, air campaigns. Include specific targets, weapon systems used, and any confirmed results.

## What Each Side Is Reporting
US/Coalition claims vs Iranian claims. What is CENTCOM/Pentagon saying? What is Iranian state media (IRNA, Press TV) saying? What is Israel reporting? Highlight contradictions and propaganda.

## Market & Economic Impact
Oil prices (Brent, WTI), stock market moves, commodity prices. How are global markets reacting? Include specific numbers (e.g., "Brent crude at $XX/barrel").

## Consumer & Supply Chain Effects
Are consumers hoarding fuel? Reports of gas station lines? Supply chain disruptions? Focus on Asia-Pacific region where fuel hoarding has been reported. Shipping route disruptions through Strait of Hormuz.

## Diplomatic Developments
Any ceasefire talks? UN statements? China/Russia positioning? Regional reactions from Gulf states? Back-channel negotiations?

## Humanitarian Situation
Civilian casualties, displacement, infrastructure damage, humanitarian aid. UNHCR/Red Cross reports. Impact on civilian populations in Iran and the region.

IMPORTANT RULES:
- Write in a professional, analytical tone — like a Reuters long-form analysis
- Use specific numbers and sources wherever possible
- If you cannot find confirmed information for a section, say "No confirmed reports in the last 24 hours" rather than making things up
- Do NOT use markdown bold (**text**) excessively — keep it readable
- Each section should be 150-250 words
- Include a brief 2-sentence opening paragraph before the first section header summarizing the day's most significant development
- End with a short "Outlook" paragraph on what to watch for tomorrow
"""


def _call_openai_text(prompt):
    """Call OpenAI Responses API with web_search for long-form TEXT (not JSON).
    Used for the daily briefing article generation."""
    if not OPENAI_API_KEY:
        return None

    request_body = json.dumps({
        "model": "gpt-5.4",
        "tools": [{"type": "web_search"}],
        "instructions": "You are a senior intelligence analyst. Write clear, detailed, professional analysis. Do NOT wrap your response in code blocks or JSON.",
        "input": prompt
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )

    try:
        print("  [Briefing] Calling OpenAI GPT-5.4 for daily briefing...")
        with urllib.request.urlopen(req, timeout=120) as resp:
            response = json.loads(resp.read().decode("utf-8"))

        text = ""
        for item in response.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text += content.get("text", "")

        if not text:
            text = response.get("output_text", "")

        if text:
            print(f"  [Briefing] Got briefing from OpenAI ({len(text)} chars)")
            return text.strip()
        else:
            print("  [Briefing] OpenAI returned empty output")
            return None

    except Exception as e:
        print(f"  [Briefing] OpenAI failed: {e}")
        return None


def _call_anthropic_text(prompt):
    """Call Anthropic Claude for long-form TEXT briefing (fallback)."""
    if not ANTHROPIC_API_KEY:
        return None

    request_body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        print("  [Briefing] Calling Claude API for daily briefing (fallback)...")
        with urllib.request.urlopen(req, timeout=90) as resp:
            response = json.loads(resp.read().decode("utf-8"))
        text = response["content"][0]["text"].strip()
        print(f"  [Briefing] Got briefing from Claude ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"  [Briefing] Claude failed: {e}")
        return None


def generate_daily_briefing(data, days):
    """Generate a daily AI briefing article. Only generates once per day.
    Returns {date, day, title, content} or None."""
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")

    # Check if today's briefing already exists
    existing = data.get("dailyBriefing", {})
    if existing.get("date") == today_str and existing.get("content"):
        print(f"  [Briefing] Today's briefing already exists ({today_str}) — skipping")
        return None

    try:
        today_formatted = now.strftime("%B %-d, %Y")
    except ValueError:
        today_formatted = now.strftime("%B %d, %Y")

    prompt = LLM_BRIEFING_PROMPT.format(today=today_formatted, day_count=days)

    # Try OpenAI first, then Claude fallback
    content = _call_openai_text(prompt)
    if not content:
        content = _call_anthropic_text(prompt)

    if not content:
        print("  [Briefing] Failed to generate briefing from any LLM")
        return None

    # Build briefing object
    briefing = {
        "date": today_str,
        "day": days,
        "title": f"Day {days} Intelligence Briefing — {today_formatted}",
        "content": content,
        "generatedAt": now.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    print(f"  [Briefing] Generated Day {days} briefing ({len(content)} chars)")
    return briefing


def apply_llm_stats(data, llm_stats):
    """
    Apply LLM-provided stats to data.json.
    Sets values DIRECTLY from GPT — no incremental logic, no min_check.
    Only updates a field if GPT provides a non-null value with a source.
    If GPT returns null for a field, the existing value is preserved.
    """
    if not llm_stats:
        return []

    updates = []
    now = datetime.now(timezone.utc)
    try:
        today = now.strftime("%b %-d, %Y")
    except ValueError:
        today = now.strftime("%b %d, %Y")

    human_cost = data.get("humanCost", {})
    banner = data.get("banner", {})

    # --- Update casualty figures — GPT says it, we use it ---
    CASUALTY_FIELDS = {
        "iranDeaths": {"key": "iranDeaths", "format": "{:,}"},
        "usKIA": {"key": "usKIA", "format": "{}"},
        "israeliDeaths": {"key": "israeliDeaths", "format": "{}"},
        "civilianDeaths": {"key": "civilianDeaths", "format": "{}"},
        "iranWounded": {"key": "iranWounded", "format": "{:,}+"},
        "gulfCasualties": {"key": "gulfCasualties", "format": "{}"},
    }

    for field, config in CASUALTY_FIELDS.items():
        stat = llm_stats.get(field)
        if not stat or stat.get("value") is None:
            print(f"    [LLM] {field}: no value returned — keeping existing")
            continue

        new_val = int(stat["value"])
        note = stat.get("note", "")
        current_str = human_cost.get(config["key"], "0")
        current = int(str(current_str).replace(",", "").replace("+", "").strip() or "0")

        formatted = config["format"].format(new_val)
        human_cost[config["key"]] = formatted
        if new_val != current:
            updates.append(f"  [LLM] {field}: {current:,} -> {new_val:,} ({note})")
        else:
            print(f"    [LLM] {field}: confirmed at {current:,} ({note})")

    # --- Update banner killed count ---
    banner_stat = llm_stats.get("bannerKilled")
    if banner_stat and banner_stat.get("value") is not None:
        banner["killed"] = f"{int(banner_stat['value']):,}+"

    # --- Update total strikes ---
    strikes_stat = llm_stats.get("totalStrikes")
    if strikes_stat and strikes_stat.get("value") is not None:
        new_strikes = int(strikes_stat["value"])
        current_str = banner.get("strikes", "0").replace("~", "").replace(",", "").replace("+", "")
        current_strikes = int(current_str) if current_str.isdigit() else 0
        banner["strikes"] = f"~{new_strikes:,}"
        if new_strikes != current_strikes:
            updates.append(f"  [LLM] strikes: ~{current_strikes:,} -> ~{new_strikes:,}")

    # --- Add new threats from LLM ---
    new_threats = llm_stats.get("newThreats", [])
    if new_threats and "threats" in data:
        existing_texts = {t.get("text", "")[:60].lower() for t in data["threats"]}
        added = 0
        for threat in new_threats:
            if isinstance(threat, str):
                threat = {"text": threat, "actor": "Unknown", "severity": "high"}
            if not isinstance(threat, dict) or not threat.get("text"):
                continue
            fingerprint = threat["text"][:60].lower()
            if fingerprint in existing_texts:
                continue

            actor_raw = threat.get("actor", "Unknown")
            data["threats"].insert(0, {
                "date": today,
                "severity": threat.get("severity", "high"),
                "actor": actor_raw.lower().split("(")[0].strip() if "(" in actor_raw else actor_raw.lower().split()[0],
                "actorLabel": actor_raw.upper(),
                "text": threat["text"],
                "target": threat.get("target", ""),
                "source": threat.get("source", "Source: LLM synthesis of recent reporting")
            })
            existing_texts.add(fingerprint)
            added += 1

        if added:
            updates.append(f"  [LLM] Added {added} new threats")
            if len(data["threats"]) > 25:
                del data["threats"][25:]

    return updates


def apply_llm_costs(data, llm_stats):
    """
    Apply LLM-provided cost model quantities to data.json.
    The LLM returns confirmed quantities for military assets (carriers deployed,
    missiles fired, sorties flown, etc.) which drive the financial cost model.

    Only updates a field if the LLM provides a non-null value with a source.
    Includes sanity-check caps as a safety net to prevent obviously wrong values,
    but the primary intelligence comes from the LLM understanding context.
    """
    if not llm_stats:
        return []

    updates = []
    cost_model = data.get("financialCost", {}).get("costModel")
    if not cost_model:
        return updates

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Safety-net caps — these are absolute physical maximums, not the primary filter.
    # The LLM should return sensible numbers; these only catch catastrophic errors.
    SAFETY_CAPS = {
        "carrier_ops": 6,
        "destroyers": 60,
        "personnel": 250000,
        "intel_cyber": 5,
        "logistics_support": 5,
        "fuel_ops": 5,
        "drone_ops": 150,
        "comms_space": 5,
        "tomahawk": 5000,
        "jdam": 25000,
        "jassm": 2500,
        "sdb": 20000,
        "b2_sorties": 200,
        "mop_bunker_busters": 30,
        "fighter_sorties": 25000,
        "interceptors": 3000,
        "prestrike_buildup": 1,
        "medical_casualty": 5,
    }

    # Cost model items the LLM can update
    COST_FIELDS = [
        "carrier_ops", "destroyers", "personnel", "drone_ops",
        "tomahawk", "jdam", "jassm", "sdb", "b2_sorties",
        "mop_bunker_busters", "fighter_sorties", "interceptors",
    ]

    # Build a lookup of cost model items by ID
    all_items = {}
    for item in cost_model.get("timeBased", []) + cost_model.get("eventBased", []):
        item_id = item.get("id", "")
        if item_id:
            all_items[item_id] = item

    for field in COST_FIELDS:
        stat = llm_stats.get(field)
        if not stat or stat.get("value") is None:
            print(f"    [LLM-Cost] {field}: no value returned -- keeping existing")
            continue

        try:
            new_val = int(stat["value"])
        except (ValueError, TypeError):
            print(f"    [LLM-Cost] {field}: invalid value '{stat.get('value')}' -- skipping")
            continue

        note = stat.get("note", "")

        # Safety cap check
        cap = SAFETY_CAPS.get(field)
        if cap and new_val > cap:
            print(f"    [LLM-Cost] WARNING: {field} value {new_val:,} exceeds safety cap {cap:,} -- clamping")
            new_val = cap

        # Don't allow zero or negative
        if new_val <= 0:
            print(f"    [LLM-Cost] {field}: value {new_val} is zero/negative -- skipping")
            continue

        # Apply to cost model
        item = all_items.get(field)
        if item:
            old_qty = item.get("quantity", 0)
            item["quantity"] = new_val
            item["lastUpdated"] = now_str
            item["source"] = f"LLM-verified ({note})"
            if new_val != old_qty:
                updates.append(f"  [LLM-Cost] {field}: {old_qty:,} -> {new_val:,} ({note})")
            else:
                print(f"    [LLM-Cost] {field}: confirmed at {old_qty:,} ({note})")
        else:
            print(f"    [LLM-Cost] {field}: not found in cost model -- skipping")

    return updates


# ============================================================
# CONFIG: RSS feeds to pull from
# ============================================================
RSS_FEEDS = [
    # Only feeds confirmed working from GitHub Actions
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "keywords": ["iran", "tehran", "irgc", "epic fury", "hezbollah", "strait of hormuz", "houthi",
                     "killed", "casualties", "deaths", "strike", "missile", "nuclear"],
        "tier": 2
    },
    {
        "name": "BBC World",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "keywords": ["iran", "israel", "us strike", "hezbollah", "houthi", "middle east",
                     "killed", "casualties", "deaths", "nuclear"],
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


def fetch_article_text(url, max_chars=3000):
    """
    Fetch the full text of an article by following its link.
    Returns plain text stripped of HTML tags, capped at max_chars.
    Used to get richer text for scanning beyond short RSS descriptions.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Strip HTML tags and get plain text
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_chars]
    except Exception as e:
        print(f"    [Debug] Failed to fetch article: {url[:60]}... ({e})")
        return ""


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

    unique = unique[:20]  # Top 20 most recent

    # Debug: show what articles we got
    print(f"  Unique articles after dedup: {len(unique)}")
    for i, item in enumerate(unique[:5]):
        print(f"    [{i+1}] {item['title'][:80]}")
        print(f"        Desc: {item['description'][:120]}...")

    # Fetch full article text for the top articles
    # This gives the scanners much richer text to work with
    print("  Fetching full article text for top articles...")
    fetched = 0
    for item in unique[:12]:  # Try top 12, stop after 8 successes
        if fetched >= 8:
            break
        link = item.get("link", "")
        if not link:
            continue
        full_text = fetch_article_text(link)
        if full_text and len(full_text) > 200:
            item["full_text"] = full_text
            fetched += 1
            print(f"    Fetched full text: {item['title'][:60]}... ({len(full_text)} chars)")
        else:
            print(f"    No text from: {item['title'][:60]}...")
    print(f"  Got full text for {fetched}/{min(len(unique), 12)} articles")

    return unique


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

    # Per-item realistic maximum quantities — prevents false positives from RSS text
    # These represent the absolute upper bound of what's physically plausible
    ITEM_MAX_CAPS = {
        # Time-based
        "carrier_ops": 6,           # US has 11 total, max 6 deployed at once
        "destroyers": 50,           # realistic cap for destroyer count
        "personnel": 200000,        # max deployed personnel
        "intel_cyber": 5,           # multiplier, not a real count
        "logistics_support": 5,
        "fuel_ops": 5,
        "drone_ops": 100,           # drone operation units, not individual drones
        "comms_space": 5,
        # Event-based
        "tomahawk": 5000,           # total US inventory ~4,000
        "jdam": 20000,
        "jassm": 2000,             # total US inventory ~2,000
        "sdb": 15000,
        "b2_sorties": 200,          # US has 20 B-2s
        "mop_bunker_busters": 200,  # total inventory ~20-30, but counting bombs not sorties
        "fighter_sorties": 20000,
        "interceptors": 2000,       # missile defense interceptors
        "prestrike_buildup": 1,     # one-time cost
        "medical_casualty": 5,
    }

    # Sanity check: clamp any existing quantities that exceed caps (fixes past false positives)
    for item in cost_model.get("timeBased", []) + cost_model.get("eventBased", []):
        item_id = item.get("id", "")
        cap = ITEM_MAX_CAPS.get(item_id)
        if cap and item.get("quantity", 0) > cap:
            old_qty = item["quantity"]
            item["quantity"] = cap
            updates.append(f"  [OpenClaw] CLAMPED {item_id}: {old_qty:,} -> {cap:,} (exceeded max cap)")

    # Scan time-based items (look for quantity changes, e.g., more carrier groups)
    for item in cost_model.get("timeBased", []):
        if not item.get("keywords"):
            continue

        item_cap = ITEM_MAX_CAPS.get(item.get("id", ""), 500)
        found = extract_number_near_keyword(
            all_text,
            item["keywords"],
            min_val=1,
            max_val=item_cap
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

        item_cap = ITEM_MAX_CAPS.get(item.get("id", ""), 5000)
        found = extract_number_near_keyword(
            all_text,
            item["keywords"],
            min_val=1,
            max_val=item_cap
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

# NOTE: scan_casualties was removed. All casualty/strike figures now come
# exclusively from GPT fact-checking in apply_llm_stats().
# The old function used regex to scan headlines for numbers, which produced
# unreliable results (e.g., inflating US KIA from 7 to 200+).


def _removed_scan_casualties():
    """REMOVED — see apply_llm_stats() instead.
    Scan RSS articles for updated casualty figures.
    Only updates a number if a HIGHER number is found (casualties only go up).
    Uses both RSS descriptions AND full article text when available.
    Returns list of updates made.
    """
    updates = []
    if not news_items:
        return updates

    # Build scanning text from RSS + full article text
    text_parts = []
    full_text_count = 0
    for item in news_items:
        text_parts.append(item["title"] + " " + item["description"])
        if "full_text" in item:
            text_parts.append(item["full_text"])
            full_text_count += 1
    all_text = " ".join(text_parts)
    print(f"    Scanning {len(news_items)} articles ({full_text_count} with full text, {len(all_text)} total chars)")

    # --- Iranian deaths ---
    iran_death_keywords = [
        "killed", "death toll", "dead", "deaths", "casualties",
        "iran killed", "iranian killed", "killed in iran",
        "iran death toll", "iranian dead", "iran casualties",
        "confirmed deaths", "killed in airstrikes", "killed in strikes",
        "reported killed", "people killed", "have been killed",
        "ministry of health", "toll", "fatalities"
    ]
    found = extract_number_near_keyword(all_text, iran_death_keywords, min_val=50, max_val=500000)
    current = int(human_cost.get("iranDeaths", "0").replace(",", "").replace("+", ""))
    if found:
        print(f"    [Debug] Iran deaths: found {found:,} in text (current: {current:,})")
        if found > current:
            human_cost["iranDeaths"] = f"{found:,}"
            updates.append(f"  [Casualties] Iranian deaths: {current:,} -> {found:,}")
        else:
            print(f"    [Debug] Iran deaths: {found:,} <= current {current:,}, no update")
    else:
        print(f"    [Debug] Iran deaths: no number found near keywords (current: {current:,})")

    # --- US KIA ---
    us_kia_keywords = [
        "us killed", "american killed", "us soldiers killed", "us troops killed",
        "us military killed", "american soldiers dead", "us service members killed",
        "us kia", "americans killed in", "us personnel killed", "american troops"
    ]
    found = extract_number_near_keyword(all_text, us_kia_keywords, min_val=1, max_val=10000)
    if found:
        current = int(human_cost.get("usKIA", "0").replace(",", "").replace("+", ""))
        print(f"    [Debug] US KIA: found {found} (current: {current})")
        if found > current:
            human_cost["usKIA"] = str(found)
            updates.append(f"  [Casualties] US KIA: {current} -> {found}")

    # --- Israeli deaths ---
    israeli_keywords = [
        "israeli killed", "israelis killed", "israeli dead", "israel deaths",
        "israeli casualties", "killed in israel"
    ]
    found = extract_number_near_keyword(all_text, israeli_keywords, min_val=1, max_val=50000)
    if found:
        current = int(human_cost.get("israeliDeaths", "0").replace(",", "").replace("+", ""))
        print(f"    [Debug] Israeli deaths: found {found} (current: {current})")
        if found > current:
            human_cost["israeliDeaths"] = str(found)
            updates.append(f"  [Casualties] Israeli deaths: {current} -> {found}")

    # --- Civilian deaths ---
    civilian_keywords = [
        "civilian killed", "civilians killed", "civilian deaths", "civilian casualties",
        "civilian death toll", "civilians dead", "civilian toll", "women and children"
    ]
    found = extract_number_near_keyword(all_text, civilian_keywords, min_val=10, max_val=500000)
    if found:
        current = int(human_cost.get("civilianDeaths", "0").replace(",", "").replace("+", ""))
        print(f"    [Debug] Civilian deaths: found {found} (current: {current})")
        if found > current:
            human_cost["civilianDeaths"] = str(found)
            updates.append(f"  [Casualties] Civilian deaths: {current} -> {found}")

    # --- Iranian wounded ---
    wounded_keywords = [
        "iranian wounded", "iran injured", "iranians injured", "injured in iran",
        "iranian hospitalized", "wounded in airstrikes", "wounded", "injured"
    ]
    found = extract_number_near_keyword(all_text, wounded_keywords, min_val=100, max_val=1000000)
    if found:
        current_str = human_cost.get("iranWounded", "0").replace(",", "").replace("+", "")
        current = int(current_str) if current_str.isdigit() else 0
        print(f"    [Debug] Iran wounded: found {found:,} (current: {current:,})")
        if found > current:
            human_cost["iranWounded"] = f"{found:,}+"
            updates.append(f"  [Casualties] Iranian wounded: {current:,} -> {found:,}")

    # --- Gulf casualties ---
    gulf_keywords = [
        "killed in kuwait", "killed in uae", "killed in saudi", "killed in bahrain",
        "gulf casualties", "gulf region deaths", "deaths in gulf"
    ]
    found = extract_number_near_keyword(all_text, gulf_keywords, min_val=1, max_val=50000)
    if found:
        current = int(human_cost.get("gulfCasualties", "0").replace(",", "").replace("+", ""))
        if found > current:
            human_cost["gulfCasualties"] = str(found)
            updates.append(f"  [Casualties] Gulf casualties: {current} -> {found}")

    return updates


def scan_strikes(news_items, banner):
    """
    Scan RSS for updated strike count numbers.
    Uses both RSS descriptions AND full article text when available.
    Returns list of updates made.
    """
    updates = []
    if not news_items:
        return updates

    text_parts = []
    for item in news_items:
        text_parts.append(item["title"] + " " + item["description"])
        if "full_text" in item:
            text_parts.append(item["full_text"])
    all_text = " ".join(text_parts)

    strike_keywords = [
        "strikes", "airstrikes", "air strikes", "sorties",
        "confirmed strikes", "total strikes", "airstrikes conducted",
        "strikes launched", "sorties flown", "bombing runs",
        "strikes on iran", "struck targets", "targets hit",
        "strike missions", "combat missions", "targets destroyed"
    ]

    # Also try with lower min_val to see what we find
    found_any = extract_number_near_keyword(all_text, strike_keywords, min_val=10, max_val=999999)
    found = extract_number_near_keyword(all_text, strike_keywords, min_val=500, max_val=999999)

    current_str = banner.get("strikes", "0").replace("~", "").replace(",", "").replace("+", "")
    try:
        current = int(current_str)
    except ValueError:
        current = 0

    if found_any:
        print(f"    [Debug] Strikes: found number {found_any:,} near keywords (threshold: 500, current: {current:,})")
    if found:
        print(f"    [Debug] Strikes: found {found:,} above threshold (current: {current:,})")
        if found > current:
            banner["strikes"] = f"~{found:,}"
            updates.append(f"  [Strikes] Total strikes: ~{current:,} -> ~{found:,}")
        else:
            print(f"    [Debug] Strikes: {found:,} <= current {current:,}, no update")
    else:
        print(f"    [Debug] Strikes: no number >= 500 found near keywords")

    return updates


def scan_threats(news_items, existing_threats):
    """
    Scan RSS articles for new threat/warning statements from key actors.
    Only adds genuinely new threats not already captured.
    Returns list of new threats added.
    """
    updates = []
    if not news_items:
        return updates

    now = datetime.now(timezone.utc)
    try:
        today = now.strftime("%b %-d, %Y")  # Linux/macOS: "Mar 6, 2026"
    except ValueError:
        today = now.strftime("%b %d, %Y")   # Windows fallback: "Mar 06, 2026"

    # Key threat actors and their keywords
    THREAT_ACTORS = {
        "IRAN (IRGC)": {
            "keywords": ["irgc", "revolutionary guard", "quds force"],
            "threat_words": ["threatens", "warned", "vowed", "pledged", "promised retaliation",
                           "will attack", "will strike", "will close", "will retaliate", "declared",
                           "retaliation", "revenge", "response"],
            "severity": "critical",
            "target_default": "US / Israel"
        },
        "IRAN (Supreme Leader)": {
            "keywords": ["khamenei", "supreme leader"],
            "threat_words": ["threatens", "warned", "fatwa", "declared", "vowed"],
            "severity": "critical",
            "target_default": "US / Israel"
        },
        "Iran": {
            "keywords": ["iran warns", "iran threatens", "iran vows", "iran retaliates",
                        "iranian threat", "tehran warns", "tehran threatens", "iran says",
                        "iran fires", "iran launches", "iran attacks", "iranian strikes"],
            "threat_words": ["warn", "threat", "retali", "vow", "attack", "strike", "launch",
                           "fire", "target", "respond", "revenge", "nuclear"],
            "severity": "high",
            "target_default": "US / Israel"
        },
        "Hezbollah": {
            "keywords": ["hezbollah", "nasrallah", "lebanon attack", "lebanon strike"],
            "threat_words": ["threatens", "warned", "vowed", "rocket", "barrage", "will attack",
                           "retaliate", "fires", "launches", "strikes", "attacks"],
            "severity": "high",
            "target_default": "Israel"
        },
        "Houthi (Ansar Allah)": {
            "keywords": ["houthi", "ansar allah", "yemen"],
            "threat_words": ["threatens", "blockade", "attack ships", "red sea", "will target",
                           "strike", "fires", "launches", "attacks", "missile"],
            "severity": "high",
            "target_default": "Red Sea shipping"
        },
        "US (Pentagon)": {
            "keywords": ["pentagon", "centcom", "secdef", "defense secretary",
                        "trump", "president trump", "white house", "us military",
                        "american forces", "us strikes", "us attacks"],
            "threat_words": ["warns", "warned", "escalation", "will respond", "overwhelming force",
                           "surrender", "no deal", "crush", "destroy", "devastating",
                           "strike", "attack", "bomb", "launch", "deploy"],
            "severity": "critical",
            "target_default": "Iran"
        },
        "IRAN (Foreign Minister)": {
            "keywords": ["iran foreign minister", "iranian foreign minister", "araghchi"],
            "threat_words": ["warns", "warned", "threatened", "consequences", "act of war"],
            "severity": "high",
            "target_default": "International"
        }
    }

    # Get existing threat text snippets to avoid duplicates
    existing_texts = set()
    for t in existing_threats:
        # Use first 60 chars of text as fingerprint
        existing_texts.add(t.get("text", "")[:60].lower())

    print(f"    Scanning {len(news_items)} articles for threats (existing: {len(existing_threats)})")

    for item in news_items:
        text = item["title"] + " " + item["description"]
        if "full_text" in item:
            text += " " + item["full_text"][:500]  # Use first 500 chars of full text for threats
        text_lower = text.lower()

        for actor, config in THREAT_ACTORS.items():
            # Check if this article mentions the actor
            actor_match = any(kw in text_lower for kw in config["keywords"])
            if not actor_match:
                continue

            # Check if this article contains threat language
            threat_match = any(tw in text_lower for tw in config["threat_words"])
            if not threat_match:
                matched_kws = [kw for kw in config["keywords"] if kw in text_lower]
                print(f"    [Debug] {actor}: actor match ({matched_kws[0]}) but no threat words in: {item['title'][:60]}")
                continue

            # Build the threat text from the article
            # Use title as the summary, clean HTML tags
            threat_text = re.sub(r'<[^>]+>', '', item["title"]).strip()

            # Skip if we already have something very similar
            fingerprint = threat_text[:60].lower()
            if fingerprint in existing_texts:
                continue

            # Determine target from text context
            target = config["target_default"]
            if "israel" in text_lower and "us" in text_lower:
                target = "US / Israel"
            elif "europe" in text_lower or "nato" in text_lower:
                target = "NATO / Europe"
            elif "red sea" in text_lower or "shipping" in text_lower:
                target = "Global shipping"
            elif "strait of hormuz" in text_lower:
                target = "Global shipping -> Strait of Hormuz"
            elif "oil" in text_lower:
                target = "Global oil supply"

            new_threat = {
                "date": today,
                "severity": config["severity"],
                "actor": actor,
                "text": threat_text,
                "target": f"Target: {target}",
                "source": f"Source: {item['source']}, {item.get('link', '')}".rstrip(", ")
            }

            existing_threats.insert(0, new_threat)  # Newest first
            existing_texts.add(fingerprint)
            updates.append(f"  [Threats] New: {actor} - {threat_text[:80]}...")

    # Cap at 25 threats
    if len(existing_threats) > 25:
        del existing_threats[25:]

    return updates


def scan_evidence(news_items, existing_evidence):
    """
    Scan RSS for new strike reports, battle damage assessments, and verifiable evidence.
    Returns list of updates made.
    """
    updates = []
    if not news_items:
        return updates

    now = datetime.now(timezone.utc)
    try:
        today = now.strftime("%b %-d, %Y")
    except ValueError:
        today = now.strftime("%b %d, %Y")

    # Evidence keywords — things that suggest verifiable, newsworthy events
    EVIDENCE_KEYWORDS = [
        "satellite imagery", "satellite images", "confirmed strike", "confirms",
        "battle damage assessment", "bda", "iaea confirms", "centcom confirms",
        "pentagon confirms", "video shows", "footage shows", "photos show",
        "verified", "intelligence assessment", "nuclear facility", "nuclear site",
        "missile launch", "intercepted", "shot down", "destroyed", "hits",
        "explosion", "school hit", "hospital hit", "struck", "bombed",
        "attack on ship", "sinks", "rescue", "first time",
        "new weapon", "prsm", "new missile", "used for the first time",
        "sailors", "warship", "damage", "crater", "rubble",
        "killed in strike", "missile hit", "targeted", "air defense",
        "nuclear", "enrichment", "uranium", "reactor",
        "carrier", "deployed", "troops land", "ground operation"
    ]

    existing_titles = set()
    for e in existing_evidence:
        existing_titles.add(e.get("title", "")[:50].lower())

    print(f"    Scanning {len(news_items)} articles for evidence (existing: {len(existing_evidence)})")
    matched_count = 0

    for item in news_items:
        text = item["title"] + " " + item["description"]
        if "full_text" in item:
            text += " " + item["full_text"][:500]
        text_lower = text.lower()

        # Must match at least one evidence keyword
        matched_kws = [kw for kw in EVIDENCE_KEYWORDS if kw in text_lower]
        if not matched_kws:
            continue

        matched_count += 1
        print(f"    [Debug] Evidence keyword match ({matched_kws[0]}): {item['title'][:70]}")

        title = re.sub(r'<[^>]+>', '', item["title"]).strip()
        fingerprint = title[:50].lower()
        if fingerprint in existing_titles:
            print(f"    [Debug] Skipped (duplicate): {title[:50]}")
            continue

        # Determine confidence level
        confidence = "medium"
        if any(w in text_lower for w in ["centcom confirms", "pentagon confirms", "satellite imagery", "iaea confirms", "verified"]):
            confidence = "high"
        elif any(w in text_lower for w in ["claims", "unverified", "alleged", "reportedly"]):
            confidence = "low"

        # Determine category
        category = "Military Strike"
        if any(w in text_lower for w in ["nuclear", "enrichment", "iaea", "uranium"]):
            category = "Nuclear"
        elif any(w in text_lower for w in ["cyber", "hack"]):
            category = "Cyber"
        elif any(w in text_lower for w in ["naval", "ship", "strait", "carrier"]):
            category = "Naval"
        elif any(w in text_lower for w in ["missile defense", "intercepted", "iron dome", "thaad"]):
            category = "Missile Defense"

        desc = re.sub(r'<[^>]+>', '', item["description"]).strip()[:250]

        new_evidence = {
            "title": title,
            "date": today,
            "confidence": confidence,
            "category": category,
            "description": desc,
            "source": item["source"],
            "link": item.get("link", "")
        }

        existing_evidence.insert(0, new_evidence)
        existing_titles.add(fingerprint)
        updates.append(f"  [Evidence] New: [{confidence}] {title[:80]}...")

    # Cap at 20 evidence items
    if len(existing_evidence) > 20:
        del existing_evidence[20:]

    print(f"    Evidence: {matched_count} keyword matches, {len(updates)} new items added")
    return updates


def update_data_json(news_items):
    """
    Update data.json with current timestamps, computed values, OpenClaw cost model,
    auto-scanned casualties, strike counts, threats, evidence, and fresh RSS developments.
    """
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

    # ---- LLM-POWERED UPDATES (replaces OpenClaw keyword scanning) ----
    # The LLM (GPT-5.4 with web search) handles ALL dynamic number updates:
    # casualties, strikes, AND cost model quantities (carriers, missiles, sorties, etc.)
    # This replaces the old OpenClaw regex scanner which caused false positives.
    cost_model = data.get("financialCost", {}).get("costModel")

    llm_stats = llm_update_stats(days, news_items=news_items, current_data=data)
    if llm_stats:
        # Apply casualty & strike updates
        print("  [LLM] Applying updated stats...")
        llm_updates = apply_llm_stats(data, llm_stats)
        if llm_updates:
            for u in llm_updates:
                print(u)
            print(f"  [LLM] Made {len(llm_updates)} casualty/strike updates")
        else:
            print("  [LLM] All casualty/strike stats confirmed -- no changes needed")

        # Apply cost model quantity updates
        print("  [LLM] Applying cost model quantities...")
        cost_updates = apply_llm_costs(data, llm_stats)
        if cost_updates:
            for u in cost_updates:
                print(u)
            print(f"  [LLM] Made {len(cost_updates)} cost model updates")
        else:
            print("  [LLM] All cost quantities confirmed -- no changes needed")
    else:
        print("  [LLM] Skipped (no API key or API call failed) -- stats unchanged")

    # ---- CALCULATE COSTS from model (always runs, uses LLM-updated quantities) ----
    if cost_model:
        total_cost, daily_burn, breakdown = calculate_costs(cost_model, days)

        data["financialCost"]["daysOfOps"] = days
        data["financialCost"]["totalCost"] = format_cost(total_cost)
        data["financialCost"]["dailyBurnRate"] = f"~{format_cost_short(daily_burn).replace('+', '')}/day"
        data["financialCost"]["breakdown"] = breakdown

        # Update banner cost
        if "banner" in data:
            data["banner"]["cost"] = format_cost_short(total_cost)

        print(f"  [Cost] Total cost: {format_cost(total_cost)} | Daily burn: {format_cost_short(daily_burn)}/day")
    else:
        # Fallback: simple formula if no cost model
        if "financialCost" in data:
            data["financialCost"]["daysOfOps"] = days
            total_billions = days
            data["financialCost"]["totalCost"] = f"${total_billions},000,000,000+"
        if "banner" in data:
            data["banner"]["cost"] = f"${days}B+"

    # ---- EVIDENCE TAB: Static nuclear evidence only (locked) ----
    # The Evidence tab is reserved for curated nuclear weapons evidence (IAEA data).
    # RSS-injected items are automatically moved to warDocumentation on the LIVE tab.
    if "evidence" in data:
        # Nuclear evidence sources that should stay
        NUCLEAR_SOURCES = ["iaea", "iiss", "isis", "intelligence assessment"]
        original_evidence = []
        war_docs = data.get("warDocumentation", [])
        moved = 0
        for item in data["evidence"]:
            source_lower = (item.get("source", "") + " " + item.get("title", "")).lower()
            is_nuclear = any(ns in source_lower for ns in NUCLEAR_SOURCES) or \
                         any(kw in source_lower for kw in ["enrichment", "stockpile", "breakout", "fordow", "uranium", "iaea"])
            if is_nuclear:
                original_evidence.append(item)
            else:
                # Move non-nuclear items to warDocumentation
                war_doc = {
                    "title": item.get("title", ""),
                    "text": item.get("description", item.get("text", "")),
                    "source": item.get("source", ""),
                    "date": item.get("date", ""),
                    "link": item.get("link", ""),
                    "category": item.get("category", "Military Strike"),
                    "confidence": item.get("confidence", "medium")
                }
                # Avoid duplicates
                existing_titles = {d.get("title", "")[:50].lower() for d in war_docs}
                if war_doc["title"][:50].lower() not in existing_titles:
                    war_docs.insert(0, war_doc)
                    moved += 1
        data["evidence"] = original_evidence
        data["warDocumentation"] = war_docs[:20]  # Cap at 20
        if moved:
            print(f"  [Evidence] Moved {moved} non-nuclear items to warDocumentation")
        print(f"  [Evidence] Locked: {len(original_evidence)} nuclear evidence items preserved")

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
                "text": f"<strong>{escape(title)}</strong> -- {escape(desc)} <span style=\"color:#64748b;font-size:11px;\">[{escape(source)}]</span>",
                "link": item.get("link", "")
            })

        if new_devs:
            existing_devs = data.get("developments", [])
            new_times = {d["time"] for d in new_devs}
            kept_existing = [d for d in existing_devs if d["time"] not in new_times]
            all_devs = new_devs + kept_existing
            data["developments"] = all_devs[:20]
            print(f"  Injected {len(new_devs)} RSS items into developments (total: {len(data['developments'])})")
    else:
        print("  No new RSS items -- keeping existing developments")

    # ---- BUILD NEWS FEED ----
    # Save full RSS items for the News Feed page (separate from developments)
    if news_items:
        new_feed = []
        for item in news_items[:100]:  # Keep up to 100 items
            try:
                dt = parsedate_to_datetime(item.get("pubDate", ""))
            except Exception:
                dt = now
            new_feed.append({
                "title": item["title"],
                "description": item.get("description", "")[:300],
                "link": item.get("link", ""),
                "source": item.get("source", "Unknown"),
                "time": dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tier": item.get("tier", 2)
            })
        # Sort by time, newest first
        new_feed.sort(key=lambda x: x["time"], reverse=True)
        # Deduplicate by title similarity
        seen_titles = set()
        unique_feed = []
        for item in new_feed:
            title_key = item["title"].lower()[:60]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_feed.append(item)
        data["newsFeed"] = unique_feed[:80]  # Cap at 80
        print(f"  Saved {len(data['newsFeed'])} items to newsFeed")

    # ---- SAVE LLM SUMMARY (stacked by day) ----
    if llm_stats and llm_stats.get("summary"):
        new_summary = llm_stats["summary"]
        data["summary"] = new_summary  # Keep latest for backward compat

        # Accumulate daily briefings — one per day, newest first
        if "briefings" not in data:
            data["briefings"] = []
        today_str = now.strftime("%Y-%m-%d")
        day_num = days
        # Check if we already have a briefing for today — update it
        found = False
        for b in data["briefings"]:
            if b.get("date") == today_str:
                b["summary"] = new_summary
                b["day"] = day_num
                found = True
                break
        if not found:
            data["briefings"].insert(0, {
                "date": today_str,
                "day": day_num,
                "summary": new_summary
            })
        # Keep last 90 days of briefings
        data["briefings"] = data["briefings"][:90]
        # Ensure newest first
        data["briefings"].sort(key=lambda x: x.get("date", ""), reverse=True)
        print(f"  Saved LLM summary to data.json (briefings: {len(data['briefings'])} days)")

    # ---- AI DAILY BRIEFING (once per day) ----
    briefing = generate_daily_briefing(data, days)
    if briefing:
        data["dailyBriefing"] = briefing

        # Archive previous briefings
        if "briefingArchive" not in data:
            data["briefingArchive"] = []

        # Add to archive if not already there
        existing_dates = {b.get("date") for b in data["briefingArchive"]}
        if briefing["date"] not in existing_dates:
            data["briefingArchive"].insert(0, briefing)

        # Cap archive at 90 days, newest first
        data["briefingArchive"].sort(key=lambda x: x.get("date", ""), reverse=True)
        data["briefingArchive"] = data["briefingArchive"][:90]
        print(f"  [Briefing] Archive: {len(data['briefingArchive'])} total briefings stored")

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
    <loc>https://www.epicfurylive.com/news.html</loc>
    <lastmod>{now}</lastmod>
    <changefreq>hourly</changefreq>
    <priority>0.8</priority>
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
    print("\n[1/7] Fetching news from RSS feeds (2 sources)...")
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

    # 5. Update data.json — LLM-driven costs + casualties + strikes + threats + evidence + developments
    print("\n[5/7] Updating data.json (LLM costs + casualties + strikes + threats + evidence + developments)...")
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
