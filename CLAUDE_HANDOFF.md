# Epic Fury Live — Claude Handoff Prompt

**Use this as context when starting a new Claude session to work on epicfurylive.com.**

---

## What This Is

Epic Fury Live (epicfurylive.com) is a free, public-service OSINT war tracker for the 2026 US-Israel-Iran conflict (Operation Epic Fury / Operation Roaring Lion). It's a single-page dashboard hosted on GitHub Pages with automated hourly updates via GitHub Actions.

**Owner:** Dan Ripoll (danrip@gmail.com, GitHub: dcrypt-007)
**Repo:** https://github.com/dcrypt-007/EpicFuryLive.git (branch: main)
**Local path:** ~/GitHub/epicfurylive
**Live site:** https://www.epicfurylive.com (GitHub Pages, custom domain with TLS via CNAME)
**User note:** Dan is not a coder. Always give complete scripts. No snippet editing or hunting for artifacts.

---

## Architecture

### Single-page app with 5 tabs:
1. **LIVE** — Threat Exchange, Homeland Threats, Theater of Operations, Latest Developments
2. **THE COST** — Human Cost (casualties), Financial Cost (OpenClaw cost model), Trend Charts, Breakdown Table, Projections
3. **HOW WE GOT HERE** — Historical timeline (1953–2026), hardcoded
4. **THE EVIDENCE** — Nuclear evidence cards, Claims Tracker, What Remains Uncertain
5. **WORLD REACTION** — US Public Opinion polls, Regional Reactions, Diplomatic Impacts

### Key design decisions:
- **data.json is the single source of truth** for ALL dynamic content. JavaScript fetches it and renders every section.
- **No framework** — plain HTML/CSS/JS. Chart.js for charts, no other dependencies.
- **Leaflet/map was removed** (user found it useless and it interfered with touchpad navigation).
- **Charts are deferred** — Chart.js cannot render on `display:none` elements, so all Cost tab charts are created on first tab visit via `window._costChartsInitialized` flag.
- GitHub Pages serves from root of main branch.

---

## File Map

```
epicfurylive/
├── index.html              # THE dashboard (~2,570 lines). All HTML + CSS + JS in one file.
├── data.json               # Single source of truth (~980 lines). ALL dynamic content lives here.
├── history.json            # Historical snapshots for trend charts. Hourly snapshots + daily summaries.
├── rss.xml                 # Auto-generated RSS feed of latest developments.
├── CNAME                   # GitHub Pages custom domain → www.epicfurylive.com
├── .nojekyll               # Tells GitHub Pages not to process with Jekyll
├── methodology.html        # Static methodology & sources page
├── glossary.html           # Static glossary page
├── sitemap.xml             # SEO sitemap
├── robots.txt              # SEO robots
├── public/
│   └── dashboard.html      # ALWAYS a sync copy of index.html (cp index.html public/dashboard.html)
├── scripts/
│   ├── update_site.py      # THE automation script (~760 lines). Runs hourly via GitHub Actions.
│   └── validate-schema.sh  # Basic HTML validation
├── .github/workflows/
│   └── update.yml          # Hourly cron at :15, runs update_site.py, commits, pushes
└── docs/                   # Supplementary docs
```

---

## data.json Structure

```
{
  "lastUpdated": "ISO timestamp",
  "dayCount": 6,
  "banner": { "strikes", "killed", "cost" },
  "humanCost": {
    counters (iranDeaths, usKIA, israeliDeaths, gulfCasualties, iranWounded, civilianDeaths),
    notes for each counter,
    "chartData": { dates[], iranDeaths[], otherDeaths[] }
  },
  "financialCost": {
    "totalCost", "dailyBurnRate", "daysOfOps",
    "costModel": {
      "timeBased": [ { id, category, unitCostPerDay, quantity, keywords[], ... } ],
      "eventBased": [ { id, category, unitCost, quantity, keywords[], ... } ]
    },
    "breakdown": [ { category, detail, cost } ],
    "projections": [ "string", ... ]
  },
  "militaryStats": { totalStrikes, missileCapabilityReduced, etc. },
  "threats": [ { date, actor, actorLabel, severity, text, target, source } ],
  "homelandThreats": [ { title, status, statusClass, date, location, text, sources } ],
  "theaterOps": [ { name, status, statusClass, description, locationsLabel, locations } ],
  "developments": [ { time (ISO), text (can contain HTML from RSS) } ],
  "mapMarkers": { strikes[], bases[], retaliation[], naval[] },  // legacy, map removed
  "evidence": [ { title, text, source } ],
  "claims": [ { actor, claim, status, statusClass } ],
  "polls": { preStrike, postStrike, byParty[], groundTroops, sources },
  "regionalReactions": [ { region, text } ],
  "diplomaticImpacts": [ "string", ... ]
}
```

---

## OpenClaw Cost Tracker (scripts/update_site.py)

OpenClaw is the automated cost-tracking engine embedded in the Python update script. It:

1. **Fetches RSS feeds** from Al Jazeera, Reuters, BBC, CNN, AP (filtered for Iran/conflict keywords)
2. **Scans article text** for numbers near cost-driving keywords using `extract_number_near_keyword()`
3. **Updates quantities** in the cost model when higher numbers are found
4. **Recalculates totals**: time-based costs (unitCostPerDay × quantity × days) + event-based costs (unitCost × quantity)
5. **Generates the breakdown table** and writes it back to data.json

### Cost model categories:
**Time-based (accumulate daily):** Carrier Strike Groups ($7M/day × 2), Destroyers ($240K/day × 13), Personnel ($500/day × 45,000), Intel/Cyber ($15M/day), Logistics ($25M/day), Fuel ($40M/day), Drones ($8M/day), Satellite/Comms ($5M/day)

**Event-based (one-time per use):** Tomahawks ($2M × 500), JDAMs ($25K × 2,000), JASSMs ($1.5M × 200), SDBs ($40K × 1,500), B-2 Sorties ($5.5M × 8), GBU-57 MOPs ($3.5M × 50), Fighter Sorties ($100K × 4,500), Interceptors ($4M × 150), Pre-strike Buildup ($630M), Medical ($50M)

### Important safeguards built in:
- **False-positive suffix filter**: Numbers followed by "pound", "lb", "kg", "percent", "billion", "million", "dollar", etc. are ignored (prevents "2,000-pound bombs" from being read as a quantity)
- **Vague quantity estimation**: "dozens" → 50, "hundreds" → 500, "scores" → 40, "several" → 5, "numerous" → 50, "multiple" → 3, "a few" → 3
- **Only updates upward**: OpenClaw only replaces a quantity if the new number is HIGHER than the current one
- **Per-category max caps**: time-based max 500,000, event-based max 100,000

### Known vulnerability:
OpenClaw can still misinterpret numbers in certain contexts. If you see a sudden cost spike, check which item's quantity changed and whether the source makes sense. The B-2 sorties were once inflated from 8 to 2,000 because "2,000-pound bombs" was misread as 2,000 sorties (now fixed with suffix filtering and tighter keywords).

---

## JavaScript Renderers (in index.html)

All sections are rendered dynamically from data.json by these functions, called in `loadLiveData()`:

```
renderThreats(data.threats)
renderHomelandThreats(data.homelandThreats)
renderTheaterOps(data.theaterOps)
renderDevelopments(data.developments)
renderEvidence(data.evidence)
renderClaims(data.claims)
renderPolls(data.polls)
renderRegionalReactions(data.regionalReactions)
renderDiplomaticImpacts(data.diplomaticImpacts)
renderBreakdown(data.financialCost.breakdown)
renderProjections(data.financialCost.projections)
```

`loadLiveData()` runs on page load and every 5 minutes via `setInterval`.

**Critical lesson learned:** If ANY renderer throws an error, ALL subsequent renderers in the `.then()` chain will fail silently. The entire site went blank when `renderTheaterOps()` called `.join()` on a string instead of an array. Always handle both data types defensively.

---

## GitHub Actions Automation

- **Cron:** Runs every hour at :15 (`15 * * * *`)
- **What it does:** Checks out repo → Runs `update_site.py` → Validates HTML → Commits and pushes if changes detected
- **Bot identity:** "Epic Fury Bot" <bot@epicfurylive.com>
- **Manual trigger:** Supports `workflow_dispatch` for on-demand runs

---

## Workflow for Making Changes

1. Edit files locally (index.html, data.json, scripts/update_site.py)
2. **ALWAYS** sync: `cp index.html public/dashboard.html`
3. `git add` the specific files changed
4. Commit with descriptive message
5. `git pull origin main --rebase` (GitHub Actions may have pushed since your last pull)
6. `git push origin main`
7. Wait 1-2 minutes for GitHub Pages deployment

---

## Common Pitfalls

1. **data.json `locations` field**: Theater ops `locations` is a STRING in data.json, not an array. The renderer handles both: `Array.isArray(t.locations) ? t.locations.join(', ') : t.locations`
2. **Charts on hidden tabs**: Chart.js renders at 0×0 on `display:none` elements. All Cost tab charts are deferred to first tab visit.
3. **OpenClaw false positives**: Always verify cost spikes. Check which quantity changed and whether the RSS source text actually supports it.
4. **Merge conflicts with GitHub Actions**: The hourly bot commits can cause push rejections. Always `git pull --rebase` before pushing.
5. **`breakdown` array**: This gets recalculated by the Python script on each run. If you edit data.json manually, update the breakdown array too or it'll show stale data until the next Actions run.
6. **Ground troops poll**: The `groundTroops` object in data.json has no `label` field. The renderer has a fallback default.
7. **public/dashboard.html**: Must always be an exact copy of index.html. Forget this and half the site breaks.
