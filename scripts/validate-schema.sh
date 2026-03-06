#!/bin/bash
# Schema / HTML Sanity Check for epicfurylive.com
# Usage: bash scripts/validate-schema.sh [path/to/file.html]

FILE="${1:-index.html}"

echo "=== Epic Fury Live — Schema & HTML Validator ==="
echo "File: $FILE"
echo ""

python3 - "$FILE" << 'PYEOF'
import re, json, sys

filepath = sys.argv[1]
html = open(filepath).read()
blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.DOTALL)

passes = 0
fails = 0
parsed = []

print("--- JSON-LD Parse Validity ---")
for i, b in enumerate(blocks, 1):
    try:
        d = json.loads(b)
        t = d.get("@type", "UNKNOWN")
        print(f"  PASS: JSON-LD block #{i} -- type: {t}")
        parsed.append(d)
        passes += 1
    except json.JSONDecodeError as e:
        print(f"  FAIL: JSON-LD block #{i} -- invalid JSON: {e}")
        fails += 1

print()
print("--- Required Fields Check ---")

def check(schema_type, field):
    global passes, fails
    for d in parsed:
        if d.get("@type") == schema_type:
            parts = field.split(".")
            obj = d
            for p in parts:
                if isinstance(obj, dict):
                    obj = obj.get(p)
                else:
                    obj = None
                    break
            if obj is not None:
                print(f"  PASS: {schema_type}.{field}")
                passes += 1
                return
    print(f"  FAIL: {schema_type}.{field} -- MISSING")
    fails += 1

check("WebSite", "name")
check("WebSite", "url")
check("WebSite", "description")
check("WebSite", "potentialAction")
check("Organization", "name")
check("Organization", "url")
check("Organization", "foundingDate")
check("LiveBlogPosting", "headline")
check("LiveBlogPosting", "datePublished")
check("LiveBlogPosting", "dateModified")
check("LiveBlogPosting", "coverageStartTime")
check("LiveBlogPosting", "publisher")
check("LiveBlogPosting", "author")
check("BreadcrumbList", "itemListElement")
check("FAQPage", "mainEntity")

print()
print("--- HTML Structure ---")

h1_count = len(re.findall(r'<h1[\s>]', html))
if h1_count >= 1:
    print(f"  PASS: h1 tags found ({h1_count})")
    passes += 1
else:
    print("  FAIL: no h1 tag found")
    fails += 1

for label, pattern in [
    ("lang attribute", 'lang="en"'),
    ("canonical link", 'rel="canonical"'),
    ("meta description", 'name="description"'),
    ("Open Graph tags", 'property="og:title"'),
    ("RSS feed link", 'application/rss+xml'),
    ("last-updated element", 'id="siteLastUpdated"'),
]:
    if pattern in html:
        print(f"  PASS: {label} present")
        passes += 1
    else:
        print(f"  FAIL: {label} missing")
        fails += 1

time_count = len(re.findall(r'<time\s', html))
if time_count >= 1:
    print(f"  PASS: <time> elements found ({time_count})")
    passes += 1
else:
    print("  FAIL: no <time> elements")
    fails += 1

print()
print(f"=== RESULTS: {passes} passed, {fails} failed ===")
print("STATUS:", "PASS" if fails == 0 else "FAIL")
sys.exit(1 if fails > 0 else 0)
PYEOF
