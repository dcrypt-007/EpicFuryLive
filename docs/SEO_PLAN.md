# SEO + AI Search Implementation Plan
## epicfurylive.com — 2026 US-Israel-Iran Conflict Tracker

---

## 1. Executive Summary

1. **Current State**: Single-page static site on GitHub Pages; minimal search visibility, untapped AI citation potential
2. **Opportunity**: War trackers are high-value search queries; AI models cite sources → direct traffic & authority
3. **Primary Goal**: Become the trusted source cited by ChatGPT, Claude, Gemini, Perplexity for factual conflict data
4. **Secondary Goal**: Rank top-10 for 50+ high-intent keywords (live updates, timelines, casualty counts, confirmed incidents)
5. **Technical Foundation**: Static site excels at speed (SEO win); add proper metadata, structured data, and information architecture
6. **Content Strategy**: Move from single page to topic cluster (home → updates → daily briefs → incident pages → source registry)
7. **Trust Signals**: Publish methodology page, source tier system, corrections log — editorial credibility attracts AI citations
8. **Distribution**: Google Search, AI search engines (Perplexity, Claude), RSS feeds, journalist outreach
9. **Timeline**: Core implementation (technical SEO + templates) in 7 days; sustainable daily updates thereafter
10. **Success Metric**: 50K+ monthly impressions + 5K+ clicks + AI citation tracking by month 3

---

## 2. Technical SEO Implementation

### 2.1 robots.txt

Create `/robots.txt` at the root of your GitHub Pages repo:

```txt
User-agent: *
Allow: /

# Google-specific crawling permissions
User-agent: Googlebot
Allow: /

# AI crawler permissions (allow Perplexity, CCbot, etc.)
User-agent: CCBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: GPTBot
Allow: /

User-agent: Claude-Web
Allow: /

# Disallow low-value crawlers
User-agent: AhrefsBot
Crawl-delay: 10

User-agent: SemrushBot
Crawl-delay: 10

# Sitemap location
Sitemap: https://epicfurylive.com/sitemap.xml
```

**Purpose**: Tell search engines which pages to crawl; explicitly welcome AI crawlers (they cite sources if they can crawl them).

---

### 2.2 Sitemap.xml Strategy

Create `/sitemap.xml` (updated automatically when you add pages):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">

  <!-- Home page (highest priority, updated daily) -->
  <url>
    <loc>https://epicfurylive.com/</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
    <news:news>
      <news:publication>
        <news:name>Epic Fury Live</news:name>
        <news:language>en</news:language>
      </news:publication>
      <news:genres>Blog</news:genres>
      <news:publication_date>2026-03-05T00:00:00Z</news:publication_date>
      <news:title>US-Israel-Iran Conflict Live Tracker</news:title>
      <news:keywords>Iran, Israel, US, military, conflict, live updates</news:keywords>
    </news:news>
  </url>

  <!-- Daily briefs (high priority, updated daily) -->
  <url>
    <loc>https://epicfurylive.com/briefs/2026-03-05/</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
    <news:news>
      <news:publication>
        <news:name>Epic Fury Live</news:name>
        <news:language>en</news:language>
      </news:publication>
      <news:publication_date>2026-03-05T00:00:00Z</news:publication_date>
      <news:title>Daily Brief: March 5, 2026</news:title>
    </news:news>
  </url>

  <!-- Updates/feed page -->
  <url>
    <loc>https://epicfurylive.com/updates/</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Incident pages -->
  <url>
    <loc>https://epicfurylive.com/incidents/</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Actors page -->
  <url>
    <loc>https://epicfurylive.com/actors/</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>

  <!-- Map page -->
  <url>
    <loc>https://epicfurylive.com/map/</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>

  <!-- Methodology (important for trust/citations) -->
  <url>
    <loc>https://epicfurylive.com/methodology/</loc>
    <lastmod>2026-03-01</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>

  <!-- Glossary -->
  <url>
    <loc>https://epicfurylive.com/glossary/</loc>
    <lastmod>2026-03-01</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>

  <!-- Corrections/changelog -->
  <url>
    <loc>https://epicfurylive.com/corrections/</loc>
    <lastmod>2026-03-05</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>

</urlset>
```

**Note for GitHub Pages**: Use a build script or GitHub Action to auto-generate this daily (update lastmod dates). Alternatively, manually update once per week.

---

### 2.3 Canonical Tags

Add to the `<head>` of every HTML page:

```html
<!-- Home page -->
<link rel="canonical" href="https://epicfurylive.com/" />

<!-- Daily brief example -->
<link rel="canonical" href="https://epicfurylive.com/briefs/2026-03-05/" />

<!-- Methodology -->
<link rel="canonical" href="https://epicfurylive.com/methodology/" />
```

**Purpose**: Tell Google which version is the "official" one. Prevents duplicate content issues if you ever publish on Medium or other platforms.

---

### 2.4 Open Graph + Twitter Card Meta Tags Template

Add this template to every page `<head>`:

```html
<!-- ========== OPEN GRAPH (for Facebook, LinkedIn, AI chatbots) ========== -->
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Epic Fury Live" />
<meta property="og:title" content="[TITLE] — US-Israel-Iran Conflict Tracker" />
<meta property="og:description" content="[DESCRIPTION]" />
<meta property="og:image" content="https://epicfurylive.com/assets/og-image-1200x630.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:url" content="https://epicfurylive.com[PAGE_PATH]" />
<meta property="og:locale" content="en_US" />

<!-- ========== TWITTER CARD ========== -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:site" content="@epicfurylive" />
<meta name="twitter:title" content="[TITLE] — US-Israel-Iran Conflict Tracker" />
<meta name="twitter:description" content="[DESCRIPTION]" />
<meta name="twitter:image" content="https://epicfurylive.com/assets/twitter-card-1024x512.png" />

<!-- ========== ARTICLE-SPECIFIC (for daily briefs, updates) ========== -->
<meta property="article:published_time" content="2026-03-05T00:00:00Z" />
<meta property="article:modified_time" content="2026-03-05T12:00:00Z" />
<meta property="article:author" content="Epic Fury Live Team" />
<meta property="article:section" content="War Tracker" />
<meta property="article:tag" content="Iran" />
<meta property="article:tag" content="Israel" />
<meta property="article:tag" content="USA" />
```

**For Homepage (index.html):**
```html
<meta property="og:type" content="website" />
<meta property="og:title" content="US-Israel-Iran Conflict: Live Tracker & Analysis" />
<meta property="og:description" content="Real-time updates on the 2026 US-Israel-Iran conflict. Confirmed incidents, casualty counts, timelines, and source methodology." />
<meta property="og:image" content="https://epicfurylive.com/assets/og-home.png" />
```

**For Daily Brief (e.g., /briefs/2026-03-05/):**
```html
<meta property="og:type" content="article" />
<meta property="og:title" content="Daily Brief: March 5, 2026 — US-Israel-Iran Conflict" />
<meta property="og:description" content="Today's key incidents, confirmed reports, and analysis. 3 airstrikes confirmed. 2 diplomatic statements. Updates ongoing." />
<meta property="article:published_time" content="2026-03-05T00:00:00Z" />
```

---

### 2.5 Title & Meta Description Conventions

**Character Limits:**
- Title tag: 50-60 characters (Google truncates at ~60 on desktop, ~50 on mobile)
- Meta description: 150-160 characters (Google truncates at ~160 on desktop, ~130 on mobile)

**Pattern Examples:**

| Page Type | Title Pattern | Meta Description Pattern |
|-----------|---|---|
| **Home** | `US-Israel-Iran Conflict: Live Tracker` (53 chars) | `Real-time updates on the 2026 conflict. Confirmed incidents, timelines, analysis, and source methodology.` (115 chars) |
| **Daily Brief** | `Daily Brief: Mar 5, 2026 \| Conflict Tracker` (47 chars) | `3 airstrikes confirmed. 2 diplomatic statements. 1 shipping incident reported. Updated hourly.` (97 chars) |
| **Incident Page** | `[Incident Title] - Confirmed \| Tracker` (41 chars) | `Location: [City]. Time: [HH:MM UTC]. Confirmed reports from [N] sources. Casualties: [X].` |
| **Methodology** | `How We Report: Source Methodology` (35 chars) | `Our editorial standards: source tiers, confidence labeling, corrections policy, and fact-checking process.` (107 chars) |
| **Glossary** | `War Tracker Glossary: Military Terms` (37 chars) | `Definitions of IRGC, hypersonic missiles, S-300, asymmetric warfare, and 50+ conflict-related terms.` (104 chars) |

**Template for Incidents:**
```
Title: [Event Type]: [Location] [Status] | Tracker
Description: [Event] on [Date]. Confirmed by [Source 1], [Source 2]. Casualties: [X]. Last update: [HH:MM UTC].
```

Example:
```
Title: Airstrike: Isfahan Drone Factory - Confirmed | Tracker
Description: US-allied airstrike reported on Iran's Shahed drone factory in Isfahan on Mar 5. Confirmed by Reuters, AP, IDF. Casualties: 2-5 estimated. Last update: 14:32 UTC.
```

---

### 2.6 Favicon + WebManifest

**Create `/favicon.ico`**: 16×16 PNG converted to ICO. Use a simple red "F" icon or conflict-relevant symbol.

**Create `/site.webmanifest`** in root:
```json
{
  "name": "Epic Fury Live - US-Israel-Iran Conflict Tracker",
  "short_name": "Epic Fury Live",
  "description": "Real-time tracker of the 2026 US-Israel-Iran conflict with confirmed incidents, timelines, and analysis.",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#dc2626",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/assets/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/assets/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/assets/icon-maskable-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "categories": ["news"],
  "screenshots": [
    {
      "src": "/assets/screenshot-540x720.png",
      "type": "image/png",
      "sizes": "540x720",
      "form_factor": "narrow"
    },
    {
      "src": "/assets/screenshot-1280x720.png",
      "type": "image/png",
      "sizes": "1280x720",
      "form_factor": "wide"
    }
  ]
}
```

**Add to `<head>`:**
```html
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#dc2626">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/assets/icon-192.png">
```

---

### 2.7 Performance (Caching, Compression, Lazy Loading)

**GitHub Pages serves all static files with aggressive caching headers by default.** But optimize further:

#### Image Optimization
- Save images as WebP + JPEG fallback
- Use images < 200KB each
- Resize to display size (don't send 4000px images for 400px displays)

**HTML Template:**
```html
<picture>
  <source srcset="/assets/map-2026-03-05.webp" type="image/webp">
  <img src="/assets/map-2026-03-05.jpg" alt="Military positions as of March 5, 2026" loading="lazy">
</picture>
```

#### Lazy Loading
- All below-the-fold images: `loading="lazy"`
- iframes (maps, embeds): `loading="lazy"`

```html
<iframe src="https://maps.example.com/embed?..." loading="lazy" title="Regional conflict map"></iframe>
```

#### JavaScript Deferral
- Load analytics last (don't block page rendering)
- Defer non-critical scripts

```html
<!-- Place before closing </body> -->
<script defer src="/assets/live-updates.js"></script>
<script defer src="/assets/analytics.js"></script>
```

#### Compression (GitHub Pages handles automatically, but verify)
- GitHub Pages GZips text by default
- Check in DevTools Network tab: "Content-Encoding: gzip"

**Target metrics:**
- Largest Contentful Paint (LCP): < 2.5 seconds
- First Input Delay (FID): < 100 milliseconds
- Cumulative Layout Shift (CLS): < 0.1

Test with: https://pagespeed.web.dev/

---

### 2.8 Accessibility (Semantic Headings, Alt Text)

**Heading Hierarchy** (never skip levels; use one H1 per page):

```html
<h1>US-Israel-Iran Conflict: Live Tracker</h1>
  <h2>Today's Key Incidents</h2>
    <h3>Airstrike: Isfahan, Iran - 14:32 UTC</h3>
    <h3>Diplomatic Statement: US Defense Secretary</h3>
  <h2>Timeline: Last 7 Days</h2>
    <h3>March 5 — Confirmed Incidents</h3>
    <h3>March 4 — Diplomatic Activity</h3>
```

**Alt Text Rules:**
- Descriptive: "Map showing Iranian and US military positions as of March 5, 2026"
- Not: "image123.png" or "map"
- For charts: "Bar chart showing estimated casualty counts by week, March-April 2026"
- For decorative images: `alt=""` (empty, tells screen readers to skip)

```html
<img src="/assets/casualties-chart.png"
     alt="Line graph: estimated casualties per week from March 2026 onwards, peaking at 1,200 on week of March 12">

<img src="/assets/logo-decoration.png"
     alt=""
     aria-hidden="true">
```

**Semantic HTML:**
```html
<article>
  <header>
    <h1>Daily Brief: March 5</h1>
    <time datetime="2026-03-05">March 5, 2026</time>
  </header>
  <section>
    <h2>Confirmed Incidents</h2>
    <ul>
      <li>Airstrike in Isfahan — 3 sources confirm</li>
    </ul>
  </section>
  <aside>
    <p><strong>Confidence:</strong> Confirmed (Tier 1 sources)</p>
  </aside>
</article>
```

---

### 2.9 Internal Linking Rules

**Linking strategy to distribute authority and guide users:**

1. **Every daily brief links to:**
   - Home page (/)
   - Incidents it references (/incidents/[incident-id]/)
   - Actors involved (/actors/iran/, /actors/usa/, etc.)
   - Related glossary terms (/glossary/#term-name)
   - Methodology (/methodology/)

2. **Incident pages link to:**
   - Actors involved (country/group profiles)
   - Related incidents (timeline)
   - Glossary definitions (military terms)
   - Sources (citations)

3. **Actor pages link to:**
   - Incidents they participated in
   - Related actors
   - Timeline of their involvement

**Example HTML:**
```html
<article>
  <h2>Airstrike: Isfahan Drone Factory</h2>
  <p>An airstrike on Iran's Shahed drone facility in
     <a href="/incidents/isfahan-shahed-march-5/">Isfahan</a>
     was confirmed by multiple sources on March 5.
  </p>
  <p>This facility has been involved in
     <a href="/incidents/?filter=shahed-production">12 prior incidents</a>.
  </p>
  <p><strong>Actors:</strong>
     <a href="/actors/usa/">United States</a>,
     <a href="/actors/israel/">Israel</a>,
     <a href="/actors/iran/">Iran</a>
  </p>
  <p><strong>Terms:</strong>
     <a href="/glossary/#shahed">Shahed drone</a>,
     <a href="/glossary/#airstrike">airstrike</a>
  </p>
  <p><a href="/methodology/">How we verify incidents</a></p>
</article>
```

**Anchor text best practices:**
- ✅ Good: `<a href="/actors/iran/">Iran's military command</a>`
- ✅ Good: `<a href="/incidents/?type=airstrike">airstrikes in the region</a>`
- ❌ Avoid: `<a href="/incidents/">click here</a>`
- ❌ Avoid: `<a href="/actors/iran/">link</a>`

---

## 3. Structured Data Templates (JSON-LD)

Add these to the `<head>` of relevant pages. JSON-LD is machine-readable and helps Google, Bing, AI models understand your content.

### 3.1 Organization (Home Page)

Add to `index.html` `<head>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Epic Fury Live",
  "alternateName": "Epic Fury",
  "url": "https://epicfurylive.com",
  "logo": "https://epicfurylive.com/assets/logo-600x400.png",
  "sameAs": [
    "https://twitter.com/epicfurylive",
    "https://linkedin.com/company/epicfurylive"
  ],
  "description": "A free public-service tracker of the 2026 US-Israel-Iran conflict with real-time updates, verified incidents, and source methodology.",
  "contact": {
    "@type": "ContactPoint",
    "contactType": "Editorial",
    "email": "info@epicfurylive.com"
  },
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Online",
    "addressCountry": "US"
  }
}
</script>
```

---

### 3.2 WebSite with SearchAction (Home Page)

Add to `index.html` `<head>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Epic Fury Live",
  "url": "https://epicfurylive.com",
  "description": "Real-time tracker of the 2026 US-Israel-Iran conflict with verified incidents, timelines, and analysis.",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://epicfurylive.com/?search={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
</script>
```

---

### 3.3 NewsArticle (Daily Brief Pages)

Add to `/briefs/YYYY-MM-DD/index.html` `<head>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "Daily Brief: March 5, 2026 — US-Israel-Iran Conflict",
  "alternativeHeadline": "Today's key incidents, confirmed reports, and diplomatic activity",
  "image": "https://epicfurylive.com/assets/brief-2026-03-05.png",
  "datePublished": "2026-03-05T00:00:00Z",
  "dateModified": "2026-03-05T18:00:00Z",
  "author": {
    "@type": "Organization",
    "name": "Epic Fury Live",
    "url": "https://epicfurylive.com"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Epic Fury Live",
    "logo": {
      "@type": "ImageObject",
      "url": "https://epicfurylive.com/assets/logo-600x400.png"
    }
  },
  "description": "Real-time updates from March 5, 2026. 3 airstrikes confirmed. 2 diplomatic statements. 1 naval incident reported.",
  "articleBody": "Full text of your brief here...",
  "articleSection": "War Tracker",
  "keywords": "Iran, Israel, USA, military, conflict, 2026",
  "inLanguage": "en-US"
}
</script>
```

---

### 3.4 BreadcrumbList (All Pages Except Home)

Add to every page except home:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://epicfurylive.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Briefs",
      "item": "https://epicfurylive.com/briefs/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "March 5, 2026",
      "item": "https://epicfurylive.com/briefs/2026-03-05/"
    }
  ]
}
</script>
```

**For Incident Pages:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://epicfurylive.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Incidents",
      "item": "https://epicfurylive.com/incidents/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Isfahan Airstrike",
      "item": "https://epicfurylive.com/incidents/isfahan-shahed-march-5/"
    }
  ]
}
</script>
```

---

### 3.5 FAQPage (Methodology Page)

Add to `/methodology/index.html`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do you verify incidents?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We use a three-tier source system: Tier 1 (official/primary sources), Tier 2 (major news outlets), Tier 3 (social media/unverified). Incidents must have at least 2 Tier 1 or 3 Tier 2 sources for confirmation. See our methodology page for details."
      }
    },
    {
      "@type": "Question",
      "name": "What does 'Confirmed' vs 'Likely' mean?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Confirmed: Multiple independent Tier 1 or credible Tier 2 sources. Likely: Consistent reports from 2+ sources but some uncertainty. Unconfirmed: Single source or claims without independent verification."
      }
    },
    {
      "@type": "Question",
      "name": "Do you correct errors?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. All corrections are logged in our Corrections page with timestamps, original claim, correction, and reason. Transparency is core to our mission."
      }
    },
    {
      "@type": "Question",
      "name": "Who funds this site?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Epic Fury Live is a volunteer-run, ad-free, donation-supported project. We have no government or corporate funding. All code and data are open-source."
      }
    }
  ]
}
</script>
```

---

### 3.6 LiveBlogPosting (Home Page + Updates Page)

Add to `index.html` and `/updates/index.html` when displaying live updates:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LiveBlogPosting",
  "headline": "US-Israel-Iran Conflict: Live Tracker",
  "description": "Real-time updates on military incidents, diplomatic activity, and analysis.",
  "datePublished": "2026-03-05T00:00:00Z",
  "dateModified": "2026-03-05T18:32:00Z",
  "image": "https://epicfurylive.com/assets/live-tracker-image.png",
  "author": {
    "@type": "Organization",
    "name": "Epic Fury Live"
  },
  "liveBlogUpdate": [
    {
      "@type": "BlogPosting",
      "headline": "Airstrike Confirmed in Isfahan",
      "datePublished": "2026-03-05T14:32:00Z",
      "dateModified": "2026-03-05T14:45:00Z",
      "author": {
        "@type": "Organization",
        "name": "Epic Fury Live"
      },
      "description": "Multiple sources confirm US-allied airstrike on Shahed drone facility.",
      "articleBody": "Full details here...",
      "url": "https://epicfurylive.com/incidents/isfahan-shahed-march-5/",
      "mentions": [
        {
          "@type": "Thing",
          "name": "Isfahan"
        },
        {
          "@type": "Thing",
          "name": "Shahed Drone"
        }
      ]
    },
    {
      "@type": "BlogPosting",
      "headline": "US Defense Secretary Statement",
      "datePublished": "2026-03-05T15:10:00Z",
      "dateModified": "2026-03-05T15:10:00Z",
      "author": {
        "@type": "Organization",
        "name": "Epic Fury Live"
      },
      "description": "Pentagon issues official response to regional military activity.",
      "url": "https://epicfurylive.com/briefs/2026-03-05/#statement-defense-secretary"
    }
  ]
}
</script>
```

---

## 4. Information Architecture — Site Map + URL Patterns

### 4.1 Complete Site Structure

```
epicfurylive.com/
├── / (Home - Live Dashboard)
├── /updates/ (Chronological feed of all updates)
├── /briefs/ (Daily summaries)
│   └── /briefs/YYYY-MM-DD/ (e.g., /briefs/2026-03-05/)
├── /incidents/ (Searchable, filterable incident database)
│   ├── /incidents/ (list + filter)
│   └── /incidents/[incident-id]/ (e.g., /incidents/isfahan-shahed-march-5/)
├── /actors/ (Countries, groups, leaders)
│   ├── /actors/ (list)
│   ├── /actors/usa/
│   ├── /actors/israel/
│   ├── /actors/iran/
│   ├── /actors/houthi/
│   └── /actors/hezbollah/
├── /map/ (Interactive map, standalone)
├── /methodology/ (Editorial standards and sourcing)
├── /glossary/ (Terms and definitions)
├── /corrections/ (Changelog of all corrections)
├── /rss.xml (RSS feed of updates)
├── /atom.xml (Atom feed alternative)
├── /robots.txt
├── /sitemap.xml
└── /404.html (custom error page)
```

---

### 4.2 URL Pattern Conventions

| Path | Purpose | Update Frequency | Example URL |
|------|---------|------------------|-------------|
| `/` | Live dashboard with current status | Hourly | `https://epicfurylive.com/` |
| `/updates/` | Chronological feed of all updates | Real-time | `https://epicfurylive.com/updates/` |
| `/updates/[update-id]/` | Individual update with sources | Real-time | `https://epicfurylive.com/updates/update-mar5-14-32/` |
| `/briefs/YYYY-MM-DD/` | Daily summary brief | Daily at 23:59 UTC | `https://epicfurylive.com/briefs/2026-03-05/` |
| `/incidents/` | Searchable incident list | Daily | `https://epicfurylive.com/incidents/?type=airstrike&country=iran` |
| `/incidents/[id]/` | Individual incident details | Weekly | `https://epicfurylive.com/incidents/isfahan-shahed-march-5/` |
| `/actors/` | List of all actors (countries, groups) | Weekly | `https://epicfurylive.com/actors/` |
| `/actors/[slug]/` | Individual country/group profile | Weekly | `https://epicfurylive.com/actors/iran/`, `/actors/irgc/` |
| `/map/` | Interactive map (fullscreen) | Daily | `https://epicfurylive.com/map/` |
| `/methodology/` | Editorial standards | Monthly | `https://epicfurylive.com/methodology/` |
| `/glossary/` | Searchable term definitions | Monthly | `https://epicfurylive.com/glossary/` |
| `/glossary/#[term]` | Anchor to specific term | Monthly | `https://epicfurylive.com/glossary/#shahed-drone` |
| `/corrections/` | Correction log (changelog) | Weekly | `https://epicfurylive.com/corrections/` |
| `/rss.xml` | RSS feed of updates | Real-time | `https://epicfurylive.com/rss.xml` |
| `/atom.xml` | Atom feed alternative | Real-time | `https://epicfurylive.com/atom.xml` |

---

### 4.3 URL Naming Conventions

**Incident IDs (slugs):**
```
[event-type]-[location]-[date][-sequence]

Examples:
- /incidents/airstrike-isfahan-march-5/
- /incidents/airstrike-isfahan-march-5-b/ (if multiple on same day)
- /incidents/naval-incident-strait-hormuz-mar-7/
- /incidents/cyber-attack-power-grid-mar-10/
- /incidents/diplomatic-statement-un-mar-3/
```

**Update IDs:**
```
/updates/[event-type]-[location]-[HH-MM-UTC]/

Examples:
- /updates/airstrike-isfahan-14-32/
- /updates/statement-pentagon-15-10/
```

**Actor slugs:**
```
/actors/[country-or-group-name-lowercase]/

Examples:
- /actors/usa/
- /actors/iran/
- /actors/israel/
- /actors/saudi-arabia/
- /actors/irgc/ (Islamic Revolutionary Guard Corps)
- /actors/quds-force/
- /actors/hezbollah/
- /actors/houthi/
```

**Glossary anchors:**
```
/glossary/#[term-lowercase-with-hyphens]

Examples:
- /glossary/#shahed-drone
- /glossary/#irgc
- /glossary/#airstrike
- /glossary/#cyber-warfare
- /glossary/#ballistic-missile
- /glossary/#hypersonic
```

---

## 5. Keyword & Query Clusters

### 5.1 Cluster: "Live Updates" Queries

**Target queries:**
- "live updates iran israel conflict"
- "us iran israel war live tracker"
- "real-time conflict updates 2026"
- "iran israel war today"
- "latest iran israel news live"

**Target page:** `/` (home) + `/updates/`

**Recommended title tag:**
```
US-Israel-Iran Conflict: Live Tracker & Updates
(55 characters)
```

**H1 pattern:**
```html
<h1>US-Israel-Iran Conflict: Live Tracker</h1>
```

**Content blocks required:**
1. **Current status snapshot** (last 6 hours)
   - Time of last update
   - Number of incidents recorded today
   - Quick summary of main events
2. **Live feed** (last 24-48 hours, reverse chronological)
   - Timestamp (UTC)
   - Headline
   - Confirmation status
   - Sources
3. **Quick filters** (search/filter by: incident type, country, date)
4. **Related links**
   - "Full timeline" (7-day)
   - "Daily brief"
   - "Interactive map"

---

### 5.2 Cluster: "Timeline" Queries

**Target queries:**
- "iran israel conflict timeline 2026"
- "us iran military conflict timeline"
- "when did the war start"
- "chronology of events iran usa israel"
- "full timeline us israel iran conflict"

**Target pages:** `/briefs/` + Daily brief pages `/briefs/YYYY-MM-DD/`

**Recommended title tag:**
```
US-Israel-Iran Conflict Timeline: Daily Briefs & Events
(56 characters)
```

**H1 pattern:**
```html
<h1>Conflict Timeline: Daily Briefings</h1>
```

**Content blocks required:**
1. **By-date listing** (most recent first, with links to full briefs)
   - Date
   - Day-of-week
   - Number of incidents that day
   - Teaser summary
2. **Month/week view** (toggleable)
3. **Key milestones** (highlighted)
4. **Filter options** (by incident type, country, severity)
5. **Quick facts** (total incidents to date, total days of conflict)

---

### 5.3 Cluster: "Map" Queries

**Target queries:**
- "iran israel conflict map 2026"
- "military positions map iran israel"
- "live map conflict middle east"
- "where are the attacks happening"
- "military bases israel iran map"

**Target page:** `/map/`

**Recommended title tag:**
```
Military Map: Iran-Israel-US Conflict Positions
(49 characters)
```

**H1 pattern:**
```html
<h1>Interactive Military Map: Real-Time Positions</h1>
```

**Content blocks required:**
1. **Embedded map** (fullscreen, mobile-responsive)
   - Zoom controls
   - Layer toggles (bases, incident locations, airspace)
   - Legend
2. **Map legend** (clear, with colors)
   - ✙ US military bases
   - 🚁 Israeli bases
   - 🎯 Confirmed incidents
   - 📍 Key cities
3. **Sidebar info**
   - "Click any marker for details"
   - "Last updated: [timestamp]"
4. **Data source attribution**
   - "Map data from [OpenStreetMap, etc.]"
5. **Related** (links to incidents, timeline, analysis)

---

### 5.4 Cluster: "What Happened Today?" Queries

**Target queries:**
- "what happened in iran israel conflict today"
- "latest developments us iran israel war"
- "today's updates middle east conflict"
- "breaking news iran israel conflict"
- "incident report iran israel march 5"

**Target page:** Daily brief (`/briefs/YYYY-MM-DD/`)

**Recommended title tag pattern:**
```
Daily Brief: [Month Day], 2026 — Conflict Updates
(e.g., "Daily Brief: March 5, 2026 — Conflict Updates")
(52 characters)
```

**H1 pattern:**
```html
<h1>Daily Brief: March 5, 2026</h1>
```

**Content blocks required:**
1. **Status header**
   - Date
   - Last update timestamp
   - Summary sentence ("3 incidents confirmed, 1 diplomatic statement")
2. **Key incidents** (in order of confirmation)
   - Headline
   - Time (UTC)
   - Confirmation status
   - Brief description
   - Sources (clickable links)
3. **Diplomatic activity** (if any)
   - Statement author
   - Key quote
   - Time issued
4. **Regional impact** (casualties, displaced people if reported)
   - Only if confirmed
   - Always include confidence level
5. **What's next** (analyst notes)
   - Expected developments
   - Watch for [specific indicators]
6. **Archive link**
   - "View previous briefs"

---

### 5.5 Cluster: "Confirmed vs Unconfirmed" Queries

**Target queries:**
- "confirmed reports iran israel conflict"
- "unconfirmed reports middle east"
- "is the report confirmed or false"
- "how to verify conflict reports"
- "reliable sources iran israel news"

**Target page:** `/methodology/` + Home page

**Recommended title tag:**
```
How We Verify Reports: Editorial Methodology
(49 characters)
```

**H1 pattern:**
```html
<h1>How We Verify: Source Methodology</h1>
```

**Content blocks required:**
1. **Confidence classification system**
   - Definition of each level
   - Examples for each
   - Why we use this system
2. **Source tier system**
   - Tier 1: Official/Primary (definitions, examples)
   - Tier 2: Major outlets (definitions, examples)
   - Tier 3: Social media/unverified (how we use)
3. **Verification process**
   - Step-by-step how we verify
   - How many sources = confirmed?
   - What makes something "likely" vs "confirmed"?
4. **Corrections policy**
   - We will correct errors
   - Link to corrections log
5. **What we won't report**
   - Single-source rumors
   - Unverified casualty claims
   - Disproven allegations

---

### 5.6 Cluster: "Casualty/Impact" Queries

**Target queries:**
- "casualties iran israel conflict march 2026"
- "death toll us iran israel war"
- "how many people died in conflict"
- "conflict impact civilian casualties"
- "estimated deaths middle east conflict"

**Target page:** `/briefs/` pages + Incidents

**Recommended title tag pattern:**
```
Casualty Tracking: Confirmed Impact Data
(40 characters)
```

**H1 pattern:**
```html
<h1>Documented Impact: Casualties & Damage</h1>
```

**Content blocks required:**
1. **Important disclaimer** (box at top)
   - We only report confirmed figures
   - Estimates are always labeled "estimated"
   - Verification requirement explanation
2. **Verified casualty summary**
   - Confirmed deaths (if any)
   - Source citations
   - Dates
   - Caveats (e.g., "final count unknown")
3. **By incident** (casualty summary for major incidents)
4. **By country** (if available)
5. **Sources for casualty data**
   - UN, governments, NGOs
   - Not speculation

---

### 5.7 Cluster: "Iran Sleeper Cells" Queries

**Target queries:**
- "iran sleeper cells us israel 2026"
- "Iranian operatives threat level"
- "iran sleeper agents us"
- "retaliatory threat iran sleeper network"

**Target page:** `/incidents/?filter=sleeper-cell` + Actors

**Recommended title tag:**
```
Iran Sleeper Cell Reports: Verified Incidents
(48 characters)
```

**H1 pattern:**
```html
<h1>Reported Sleeper Cell Activity: Verified Incidents</h1>
```

**Content blocks required:**
1. **Verification note** (crucial)
   - These reports are sensitive
   - Only including officially reported incidents
   - Avoiding speculation
2. **Confirmed incidents** (if any exist)
   - Source: official government statement
   - Verification: [Tier 1, government]
   - Details: what, when, where, outcome
3. **Threat assessments**
   - Links to official statements
   - No speculation
4. **Related**: Iran actors page, IRGC Quds Force details

---

### 5.8 Cluster: "Iran Nuclear Program" Queries

**Target queries:**
- "iran nuclear program 2026"
- "iran nuclear threat conflict"
- "nuclear facilities targeted"
- "iran enrichment status"

**Target page:** `/glossary/#iran-nuclear-program` + Actors

**Recommended title tag:**
```
Iran Nuclear Program: Status & Incidents
(41 characters)
```

**H1 pattern:**
```html
<h1>Iran's Nuclear Program: Key Context</h1>
```

**Content blocks required:**
1. **Background** (2-3 sentences)
   - Current enrichment status
   - Known facilities
2. **Incidents involving nuclear facilities**
   - List with links
3. **International statements** (IAEA, US, etc.)
   - Citations only, no speculation
4. **Glossary terms** (links)
   - Enrichment level
   - Centrifuges
   - IAEA inspections

---

### 5.9 Cluster: "Operation Epic Fury" Queries

**Target queries:**
- "operation epic fury"
- "epic fury iran retaliation"
- "operation epic fury missiles"
- "what is operation epic fury"

**Target page:** `/incidents/operation-epic-fury/` + Actors

**Recommended title tag:**
```
Operation Epic Fury: Iran's Response Campaign
(48 characters)
```

**H1 pattern:**
```html
<h1>Operation Epic Fury: Iran's Retaliation Campaign</h1>
```

**Content blocks required:**
1. **Overview**
   - What is it (Iranian military campaign)
   - When announced
   - Official source
2. **Timeline of Operation Epic Fury incidents**
   - Each confirmed strike
   - Missiles used
   - Targets
   - Results
3. **Response from US, Israel, allies**
4. **Impact assessment**
   - Damage confirmed
   - Casualties (if any)
5. **Related incidents**

---

### 5.10 Cluster: "US-Iran War Cost" Queries

**Target queries:**
- "us iran war cost 2026"
- "economic impact middle east conflict"
- "oil prices iran israel conflict"
- "military spending conflict budget"

**Target page:** `/briefs/` with analysis + separate analysis page

**Recommended title tag:**
```
Conflict Cost Analysis: Economic Impact
(41 characters)
```

**H1 pattern:**
```html
<h1>Conflict Cost: Economic & Strategic Analysis</h1>
```

**Content blocks required:**
1. **Verified economic impacts**
   - Oil market movement (cite prices)
   - Shipping disruption (if any)
   - Official government spending announcements
2. **Military expenditure**
   - Official statements only
3. **Humanitarian costs**
   - Documented displacement
   - Infrastructure damage (verified)
4. **Warnings against speculation**
   - "Total cost estimates vary widely; we report confirmed figures only"
5. **Sources**
   - Official statements
   - Reputable economic analysts
   - News sources (Tier 2)

---

## 6. AI-Search-Ready Content Templates (HTML)

AI search engines (Perplexity, Claude.com, etc.) cite sources when they can find well-structured, semantically marked up content. These templates make that easy.

### 6.1 Live Update Entry Block

Use this HTML structure for every update in the live feed:

```html
<article class="live-update" id="update-mar5-14-32" data-timestamp="2026-03-05T14:32:00Z">

  <header>
    <time datetime="2026-03-05T14:32:00Z">14:32 UTC</time>
    <h3>Airstrike Reported: Isfahan, Iran</h3>
  </header>

  <div class="update-summary">
    <p>Multiple military and news sources reported an airstrike on a drone production facility in Isfahan, Iran on March 5 at approximately 14:32 UTC (local time 18:02).</p>
  </div>

  <div class="incident-details">
    <dl>
      <dt>Location</dt>
      <dd><a href="/map/?location=isfahan">Isfahan, Iran</a> — Shahed Drone Production Facility</dd>

      <dt>Type</dt>
      <dd><a href="/glossary/#airstrike">Airstrike</a></dd>

      <dt>Time (UTC)</dt>
      <dd>14:32</dd>

      <dt>Time (Local)</dt>
      <dd>18:02 Iran Standard Time</dd>

      <dt>Confidence</dt>
      <dd><span class="confidence-confirmed">Confirmed</span></dd>

      <dt>Casualties</dt>
      <dd><span class="confidence-unconfirmed">Unconfirmed</span> — Reports range from 0-5</dd>

      <dt>Facility</dt>
      <dd><a href="/glossary/#shahed">Shahed 136/131 Kamikaze Drone</a> production site</dd>
    </dl>
  </div>

  <section class="sources">
    <h4>Sources</h4>
    <ol>
      <li>
        <strong>[Tier 1 — Official]</strong>
        <a href="https://www.idf.il/en/media-hub/official-statements/...">IDF Official Statement</a>
        <time datetime="2026-03-05T14:45:00Z">14:45 UTC</time>
        — "Confirmed strike on terror infrastructure"
      </li>
      <li>
        <strong>[Tier 1 — Official]</strong>
        <a href="https://www.defense.gov/News/Releases/Release/...">US Department of Defense</a>
        <time datetime="2026-03-05T15:00:00Z">15:00 UTC</time>
        — "US military conducted precision strike on weapons facility"
      </li>
      <li>
        <strong>[Tier 2 — Major Outlet]</strong>
        <a href="https://www.reuters.com/world/...">Reuters: "Airstrike on Isfahan Drone Plant Confirmed"</a>
        <time datetime="2026-03-05T14:50:00Z">14:50 UTC</time>
      </li>
      <li>
        <strong>[Tier 2 — Major Outlet]</strong>
        <a href="https://apnews.com/...">AP News: "Iran's Drone Plant Hit"</a>
        <time datetime="2026-03-05T15:05:00Z">15:05 UTC</time>
      </li>
    </ol>
  </section>

  <section class="analysis">
    <h4>Context & Analysis</h4>
    <p>
      The Shahed facility is one of Iran's primary drone production centers.
      <a href="/actors/iran/">Iran</a> has used Shahed drones extensively
      <a href="/incidents/?filter=shahed-attacks">in 12+ documented incidents</a>
      since the conflict began. Damage assessment is ongoing.
      <a href="/methodology/">See our verification methodology.</a>
    </p>
  </section>

  <footer class="update-meta">
    <p>
      <small>
        Last updated: <time datetime="2026-03-05T15:30:00Z">15:30 UTC</time><br>
        Updates to this incident: <a href="#update-mar5-15-30">+2 more</a><br>
        <a href="/incidents/isfahan-shahed-march-5/">Full incident page</a>
      </small>
    </p>
  </footer>

</article>
```

**Key SEO features:**
- `datetime` attributes for machine-readability
- Semantic markup (`<time>`, `<article>`, `<dl>`, `<section>`)
- Clear source tier labeling
- Confidence classification
- Internal links to actors, glossary, methodology
- Structured incident metadata (location, type, casualties)

---

### 6.2 Daily Brief Page Template

Create `/briefs/2026-03-05/index.html` using this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Brief: March 5, 2026 — US-Israel-Iran Conflict Tracker</title>
  <meta name="description" content="March 5, 2026 summary: 3 airstrikes confirmed, 2 diplomatic statements, 1 shipping incident. Real-time updates and verified sources.">

  <!-- Open Graph + Twitter -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="Daily Brief: March 5, 2026 — US-Israel-Iran Conflict">
  <meta property="og:description" content="Today's summary: 3 airstrikes confirmed, 2 diplomatic statements. Read verified updates.">
  <meta property="og:image" content="https://epicfurylive.com/assets/brief-2026-03-05.png">
  <meta property="og:url" content="https://epicfurylive.com/briefs/2026-03-05/">
  <meta property="article:published_time" content="2026-03-05T00:00:00Z">
  <meta property="article:modified_time" content="2026-03-05T23:59:00Z">
  <meta property="article:author" content="Epic Fury Live">
  <meta property="article:section" content="War Tracker">
  <meta property="article:tag" content="Iran">
  <meta property="article:tag" content="Israel">
  <meta property="article:tag" content="USA">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Daily Brief: March 5, 2026">
  <meta name="twitter:description" content="3 airstrikes confirmed, 2 diplomatic statements, 1 shipping incident.">
  <meta name="twitter:image" content="https://epicfurylive.com/assets/twitter-brief-2026-03-05.png">

  <!-- Canonical + Structured Data -->
  <link rel="canonical" href="https://epicfurylive.com/briefs/2026-03-05/">

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "Daily Brief: March 5, 2026 — US-Israel-Iran Conflict",
    "image": "https://epicfurylive.com/assets/brief-2026-03-05.png",
    "datePublished": "2026-03-05T00:00:00Z",
    "dateModified": "2026-03-05T23:59:00Z",
    "author": {
      "@type": "Organization",
      "name": "Epic Fury Live",
      "url": "https://epicfurylive.com"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Epic Fury Live",
      "logo": {
        "@type": "ImageObject",
        "url": "https://epicfurylive.com/assets/logo-600x400.png"
      }
    },
    "description": "Real-time updates from March 5, 2026. 3 airstrikes confirmed. 2 diplomatic statements. 1 naval incident reported.",
    "articleBody": "[Article text]",
    "articleSection": "War Tracker",
    "keywords": "Iran, Israel, USA, military, conflict, 2026",
    "inLanguage": "en-US"
  }
  </script>

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://epicfurylive.com"
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "Daily Briefs",
        "item": "https://epicfurylive.com/briefs/"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": "March 5, 2026",
        "item": "https://epicfurylive.com/briefs/2026-03-05/"
      }
    ]
  }
  </script>
</head>

<body>

<article class="daily-brief">
  <header>
    <h1>Daily Brief: March 5, 2026</h1>
    <p class="brief-meta">
      <time datetime="2026-03-05">March 5, 2026</time> —
      Last update: <time datetime="2026-03-05T23:59:00Z">23:59 UTC</time>
    </p>
    <p class="brief-summary">
      <strong>Summary:</strong> 3 airstrikes confirmed. 2 diplomatic statements. 1 shipping incident reported.
      <a href="/methodology/">How we verify reports.</a>
    </p>
  </header>

  <nav class="brief-sections">
    <ul>
      <li><a href="#confirmed-incidents">Confirmed Incidents (3)</a></li>
      <li><a href="#diplomatic">Diplomatic Activity (2)</a></li>
      <li><a href="#maritime">Maritime/Shipping</a></li>
      <li><a href="#analyst-notes">Analyst Notes</a></li>
    </ul>
  </nav>

  <!-- CONFIRMED INCIDENTS SECTION -->
  <section id="confirmed-incidents">
    <h2>Confirmed Incidents</h2>

    <!-- Incident 1: Isfahan Airstrike -->
    <article class="incident-brief">
      <h3>1. Airstrike: Isfahan Drone Facility</h3>
      <dl class="incident-metadata">
        <dt>Time (UTC)</dt>
        <dd><time datetime="2026-03-05T14:32:00Z">14:32</time></dd>
        <dt>Location</dt>
        <dd><a href="/map/?location=isfahan">Isfahan, Iran</a> — Shahed drone production</dd>
        <dt>Confidence</dt>
        <dd><span class="badge confirmed">Confirmed</span></dd>
        <dt>Sources</dt>
        <dd>
          <a href="https://www.idf.il/...">IDF Official</a> •
          <a href="https://www.defense.gov/...">DoD</a> •
          <a href="https://www.reuters.com/...">Reuters</a>
        </dd>
      </dl>
      <p>
        Multiple sources confirmed a precision airstrike on Iran's Shahed drone production facility in Isfahan.
        <a href="/incidents/isfahan-shahed-march-5/">Full incident details →</a>
      </p>
    </article>

    <!-- Incident 2 -->
    <article class="incident-brief">
      <h3>2. Missile Strike: Tactical Base near Syria Border</h3>
      <dl class="incident-metadata">
        <dt>Time (UTC)</dt>
        <dd><time datetime="2026-03-05T11:15:00Z">11:15</time></dd>
        <dt>Location</dt>
        <dd>Northern Iran, Syria border region</dd>
        <dt>Confidence</dt>
        <dd><span class="badge confirmed">Confirmed</span></dd>
      </dl>
      <p>
        Israeli military reported strike on tactical command facility. Damage assessment ongoing.
        <a href="/incidents/tactical-base-march-5/">Full details →</a>
      </p>
    </article>

    <!-- Incident 3 -->
    <article class="incident-brief">
      <h3>3. Cyber Incident: Energy Sector Systems</h3>
      <dl class="incident-metadata">
        <dt>Time (UTC)</dt>
        <dd><time datetime="2026-03-05T08:00:00Z">~08:00</time> (reported later)</dd>
        <dt>Type</dt>
        <dd><a href="/glossary/#cyber-warfare">Cyber attack</a></dd>
        <dt>Confidence</dt>
        <dd><span class="badge confirmed">Confirmed</span></dd>
        <dt>Attribution</dt>
        <dd><span class="badge unconfirmed">Unconfirmed</span> — attributed by analysis, not official statement</dd>
      </dl>
      <p>
        Suspected cyber intrusion in Iranian energy infrastructure reported by cybersecurity researchers.
        No operational outages confirmed.
        <a href="/incidents/cyber-energy-march-5/">Full details →</a>
      </p>
    </article>

  </section>

  <!-- DIPLOMATIC SECTION -->
  <section id="diplomatic">
    <h2>Diplomatic Activity</h2>

    <article class="diplomatic-update">
      <h3>US Defense Secretary Statement</h3>
      <time datetime="2026-03-05T15:00:00Z">15:00 UTC</time>
      <blockquote cite="https://www.defense.gov/...">
        "The United States and our allies have conducted proportional defensive operations against Iranian weapons facilities. We remain committed to de-escalation and regional stability."
      </blockquote>
      <p>
        <a href="https://www.defense.gov/News/Releases/...">Full statement →</a>
      </p>
    </article>

    <article class="diplomatic-update">
      <h3>UN Security Council Emergency Session Called</h3>
      <time datetime="2026-03-05T16:30:00Z">16:30 UTC</time>
      <p>
        Russia and China requested an emergency UN Security Council session to discuss the March 5 incidents.
        Session scheduled for March 6 at 10:00 UTC.
      </p>
      <p>
        <a href="https://news.un.org/...">UN News Report →</a>
      </p>
    </article>

  </section>

  <!-- MARITIME SECTION -->
  <section id="maritime">
    <h2>Maritime & Shipping</h2>

    <article class="maritime-update">
      <h3>Shipping Alert: Strait of Hormuz</h3>
      <p>
        <a href="/glossary/#strait-hormuz">Strait of Hormuz</a> transit disruptions reported due to heightened military activity.
        <a href="https://www.marinetraffic.com/">MarineTraffic</a> shows 3 vessels rerouting around the Arabian Peninsula.
      </p>
      <p>
        Oil prices jumped 2.3% on shipping concerns.
      </p>
    </article>

  </section>

  <!-- ANALYST NOTES -->
  <section id="analyst-notes">
    <h2>Analyst Notes</h2>
    <div class="analysis-box">
      <h3>What to Watch for Next:</h3>
      <ul>
        <li><strong>Iran Response:</strong> Will Iran conduct retaliation strikes? Historical precedent suggests 24-72 hour window.</li>
        <li><strong>Escalation Signals:</strong> Monitor for mobilization of <a href="/actors/irgc/">IRGC</a> or <a href="/actors/quds-force/">Quds Force</a> assets.</li>
        <li><strong>Diplomacy:</strong> UN session on March 6 may shift dynamics.</li>
        <li><strong>Oil Markets:</strong> Shipping disruptions could push prices higher if sustained.</li>
      </ul>
    </div>

    <div class="methodology-note">
      <p>
        <small>
          <strong>Note on confidence levels:</strong>
          <span class="badge confirmed">Confirmed</span> = Multiple Tier 1 or credible Tier 2 sources.
          <a href="/methodology/">Learn our verification system.</a>
        </small>
      </p>
    </div>
  </section>

  <!-- FOOTER / NAVIGATION -->
  <footer class="brief-footer">
    <nav>
      <ul>
        <li><a href="/briefs/">← Previous Briefs</a></li>
        <li><a href="/briefs/2026-03-06/">Next Brief (March 6) →</a></li>
        <li><a href="/updates/">Live Updates Feed</a></li>
        <li><a href="/incidents/">Full Incidents Database</a></li>
      </ul>
    </nav>
  </footer>

</article>

</body>
</html>
```

---

### 6.3 Incident Page Template

Create `/incidents/[incident-id]/index.html` using this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Isfahan Airstrike: Shahed Facility - March 5, 2026 | Tracker</title>
  <meta name="description" content="Detailed report of the confirmed airstrike on Isfahan Shahed drone facility on March 5, 2026. Sources, timeline, and analysis.">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="Isfahan Airstrike: Shahed Facility - March 5, 2026">
  <meta property="og:description" content="Confirmed airstrike on Iran's drone facility. Multiple sources, timeline, and analysis.">
  <meta property="og:image" content="https://epicfurylive.com/assets/isfahan-facility-image.png">
  <meta property="article:published_time" content="2026-03-05T14:32:00Z">
  <meta property="article:modified_time" content="2026-03-05T18:00:00Z">

  <link rel="canonical" href="https://epicfurylive.com/incidents/isfahan-shahed-march-5/">

  <!-- Schema markup -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "Airstrike on Isfahan Shahed Drone Facility - March 5, 2026",
    "datePublished": "2026-03-05T14:32:00Z",
    "dateModified": "2026-03-05T18:00:00Z",
    "author": {
      "@type": "Organization",
      "name": "Epic Fury Live"
    },
    "image": "https://epicfurylive.com/assets/isfahan-facility-image.png"
  }
  </script>
</head>

<body>

<article class="incident-page">
  <header>
    <h1>Airstrike: Isfahan Shahed Facility</h1>
    <dl class="incident-header-info">
      <dt>Date</dt>
      <dd><time datetime="2026-03-05">March 5, 2026</time></dd>

      <dt>Time (UTC)</dt>
      <dd><time datetime="2026-03-05T14:32:00Z">14:32</time></dd>

      <dt>Location</dt>
      <dd>Isfahan, Iran — Shahed Drone Production Facility</dd>

      <dt>Coordinates</dt>
      <dd>32.6539°N, 51.6660°E (on map: <a href="/map/?zoom=14&lat=32.6539&lng=51.6660">view</a>)</dd>

      <dt>Status</dt>
      <dd><span class="badge-large confirmed">CONFIRMED</span></dd>
    </dl>
  </header>

  <!-- OVERVIEW -->
  <section id="overview">
    <h2>Overview</h2>
    <p>
      Multiple independent sources confirmed a precision airstrike on Iran's Shahed-136/131 kamikaze drone production facility
      in Isfahan on March 5, 2026 at approximately 14:32 UTC (18:02 Iran Standard Time).
    </p>
    <p>
      Damage assessment ongoing. <span class="confidence-unconfirmed">Unconfirmed</span> reports of 2-5 casualties.
    </p>
  </section>

  <!-- TIMELINE -->
  <section id="timeline">
    <h2>Incident Timeline</h2>
    <ol class="timeline">
      <li>
        <time datetime="2026-03-05T14:32:00Z">14:32 UTC</time>
        — Airstrike reported by Iranian media and international observers
      </li>
      <li>
        <time datetime="2026-03-05T14:45:00Z">14:45 UTC</time>
        — <strong>IDF Official Statement:</strong> Confirmed strike on "terror infrastructure in Isfahan"
      </li>
      <li>
        <time datetime="2026-03-05T15:00:00Z">15:00 UTC</time>
        — <strong>US DoD Statement:</strong> "US military conducted precision strike on weapons facility supporting Iranian military operations"
      </li>
      <li>
        <time datetime="2026-03-05T15:30:00Z">15:30 UTC</time>
        — Reuters, AP News, BBC confirm via ground sources and satellite imagery
      </li>
      <li>
        <time datetime="2026-03-05T16:00:00Z">16:00 UTC</time>
        — Damage assessment photos released; facility appears substantially damaged
      </li>
      <li>
        <time datetime="2026-03-05T17:30:00Z">17:30 UTC</time>
        — <strong>Iran IRNA Statement:</strong> "Confirmed damage to facility; defensive systems engaged attackers" (no hits claimed)
      </li>
    </ol>
  </section>

  <!-- SOURCES -->
  <section id="sources">
    <h2>Source Documentation</h2>

    <h3>Tier 1 — Official Sources</h3>
    <ul class="source-list">
      <li>
        <strong>Israeli Defense Forces (IDF)</strong>
        <time datetime="2026-03-05T14:45:00Z">14:45 UTC</time><br>
        Official statement: <a href="https://www.idf.il/en/media-hub/official-statements/...">Link to IDF site</a><br>
        <blockquote>"Confirmed strike on terror infrastructure in Isfahan"</blockquote>
      </li>
      <li>
        <strong>US Department of Defense</strong>
        <time datetime="2026-03-05T15:00:00Z">15:00 UTC</time><br>
        Press release: <a href="https://www.defense.gov/News/Releases/...">Link to DoD site</a><br>
        <blockquote>"US military conducted precision strike on weapons facility supporting Iranian military operations"</blockquote>
      </li>
      <li>
        <strong>Iran Islamic Republic News Agency (IRNA)</strong>
        <time datetime="2026-03-05T17:30:00Z">17:30 UTC</time><br>
        Official report: <a href="https://www.irna.ir/...">Link to IRNA site</a><br>
        <blockquote>"Confirmed damage to facility; defensive systems engaged attackers"</blockquote>
      </li>
    </ul>

    <h3>Tier 2 — Major News Outlets</h3>
    <ul class="source-list">
      <li><strong>Reuters:</strong> <a href="https://www.reuters.com/world/...">"Airstrike on Isfahan drone plant confirmed"</a></li>
      <li><strong>AP News:</strong> <a href="https://apnews.com/...">"Iran's Shahed Drone Facility Hit in Strike"</a></li>
      <li><strong>BBC:</strong> <a href="https://www.bbc.com/news/...">"Isfahan Facility Damaged in Military Operation"</a></li>
      <li><strong>Al Jazeera:</strong> <a href="https://www.aljazeera.com/...">"Multiple Sources Confirm Isfahan Strike"</a></li>
    </ul>

    <h3>Tier 3 — Analysis & Social Media</h3>
    <ul class="source-list">
      <li><strong>Satellite Imagery (MAXAR):</strong> <a href="https://www.maxar.com/">Before/after images available</a></li>
      <li><strong>Military Analysts (Twitter/X):</strong> @JanesMIL, @markito0171, @ConflictNews provide analysis</li>
    </ul>
  </section>

  <!-- FACILITY BACKGROUND -->
  <section id="background">
    <h2>Facility Background</h2>
    <p>
      The Isfahan facility is one of <a href="/actors/iran/">Iran's</a> primary production centers for
      <a href="/glossary/#shahed-drone">Shahed-136 and Shahed-131 kamikaze drones</a>.
      These weapons have been documented in
      <a href="/incidents/?filter=shahed-attacks">12+ prior incidents</a>
      since the conflict began.
    </p>
    <dl>
      <dt>Facility Name</dt>
      <dd>Isfahan Drone Production Complex (also called "Shahed Manufacturing")</dd>

      <dt>Location</dt>
      <dd>Isfahan, central Iran</dd>

      <dt>Production Capacity</dt>
      <dd>Estimated 50-100 drones per month (unconfirmed)</dd>

      <dt>Prior Incidents</dt>
      <dd><a href="/incidents/?filter=shahed">12 documented attacks on Shahed production/storage</a></dd>
    </dl>
  </section>

  <!-- DAMAGE ASSESSMENT -->
  <section id="damage">
    <h2>Damage Assessment</h2>
    <p>
      <span class="confidence-confirmed">Confirmed:</span> Facility sustained significant structural damage.
    </p>
    <ul>
      <li>Main production building: destroyed or heavily damaged</li>
      <li>Assembly lines: partially operational (assessment ongoing)</li>
      <li>Storage: 2+ secondary explosions reported</li>
    </ul>
    <p>
      <span class="confidence-unconfirmed">Unconfirmed:</span> Satellite imagery suggests 40-60% facility damage.
    </p>
    <p>
      <a href="https://www.maxar.com/">MAXAR satellite imagery available here</a> for professional analysis.
    </p>
  </section>

  <!-- CASUALTIES -->
  <section id="casualties">
    <h2>Casualties</h2>
    <p class="important-note">
      <strong>Note:</strong> We only report confirmed casualty figures. Estimates vary widely and should not be treated as definitive.
    </p>
    <p>
      <span class="confidence-unconfirmed">Unconfirmed</span> — Reported range: 0-5 fatalities.
    </p>
    <ul>
      <li>Iran claims minimal casualties (official statement pending)</li>
      <li>Social media reports (unverified) claim higher numbers</li>
      <li>Satellite imagery cannot determine casualty count</li>
    </ul>
    <p>
      <em>We will update this section when official casualty figures are released.</em>
    </p>
  </section>

  <!-- ANALYSIS -->
  <section id="analysis">
    <h2>Strategic Analysis</h2>
    <p>
      <strong>Significance:</strong> This strike targets Iran's drone production capacity, a core component of Iran's
      <a href="/actors/iran/">asymmetric warfare capability</a>. Production disruption could affect Iran's ability to
      conduct future <a href="/incidents/operation-epic-fury/">Operation Epic Fury</a> style retaliatory operations.
    </p>
    <p>
      <strong>Timing:</strong> Airstrike follows
      <a href="/incidents/?filter=cyber">March 5 cyber incidents</a>
      and continued diplomatic tension.
    </p>
    <p>
      <strong>What's Next:</strong> Watch for Iranian retaliation response (typically 24-72 hour window based on
      <a href="/incidents/?filter=iran-response">historical patterns</a>).
    </p>
  </section>

  <!-- RELATED INCIDENTS -->
  <section id="related">
    <h2>Related Incidents</h2>
    <ul>
      <li><a href="/incidents/isfahan-textile-march-2/">Isfahan Textile Facility - March 2</a></li>
      <li><a href="/incidents/?filter=shahed">All Shahed Drone-Related Incidents (12)</a></li>
      <li><a href="/incidents/?filter=iran-airstrikes">Airstrikes on Iran (7 this month)</a></li>
    </ul>
  </section>

  <!-- CORRECTIONS / UPDATES -->
  <section id="updates">
    <h2>Updates & Corrections</h2>
    <p>
      <em>This incident page will be updated as new information becomes available.</em>
    </p>
    <ul>
      <li><time datetime="2026-03-05T15:00:00Z">15:00 UTC</time> — DoD statement added</li>
      <li><time datetime="2026-03-05T16:00:00Z">16:00 UTC</time> — Satellite imagery and damage assessment added</li>
      <li><time datetime="2026-03-05T17:30:00Z">17:30 UTC</time> — Iran IRNA statement added</li>
    </ul>
    <p>
      Corrections will be logged in our <a href="/corrections/">corrections page</a>.
    </p>
  </section>

  <!-- METHODOLOGY -->
  <section id="methodology">
    <h2>How We Verified This</h2>
    <p>
      This incident is marked <span class="badge-large confirmed">CONFIRMED</span> because:
    </p>
    <ol>
      <li>Official Tier 1 statements from both US DoD and IDF</li>
      <li>Confirmation from Iranian government (IRNA)</li>
      <li>Independent verification by major news outlets (Reuters, AP, BBC)</li>
      <li>Supporting satellite imagery from MAXAR</li>
    </ol>
    <p>
      <a href="/methodology/">Learn about our verification system →</a>
    </p>
  </section>

  <!-- FOOTER NAVIGATION -->
  <footer class="incident-footer">
    <nav>
      <ul>
        <li><a href="/briefs/2026-03-05/">← Back to Daily Brief</a></li>
        <li><a href="/incidents/">← Incidents List</a></li>
        <li><a href="/map/?incident=isfahan-shahed-march-5">View on Map →</a></li>
      </ul>
    </nav>
  </footer>

</article>

</body>
</html>
```

---

### 6.4 Confidence System Definition

Use this classification consistently across all pages:

```html
<div class="confidence-system">
  <h3>Confidence Levels</h3>

  <div class="confidence-level confirmed">
    <h4>✓ Confirmed</h4>
    <p>
      <strong>Requirement:</strong> Multiple independent sources from Tier 1 (official/primary)
      OR 3+ credible Tier 2 (major outlets) sources reporting the same core facts.
    </p>
    <p><strong>Examples:</strong></p>
    <ul>
      <li>Official government statement + major news outlets</li>
      <li>Multiple news agencies (Reuters, AP, BBC) independently confirming</li>
      <li>Military statement + satellite imagery</li>
    </ul>
    <p><strong>Color/Badge:</strong> <span class="badge confirmed">Confirmed</span></p>
  </div>

  <div class="confidence-level likely">
    <h4>~ Likely</h4>
    <p>
      <strong>Requirement:</strong> Consistent reports from 2+ credible sources but some ambiguity or
      minor source conflicts. Likely accurate but not definitively confirmed.
    </p>
    <p><strong>Examples:</strong></p>
    <ul>
      <li>Two major news outlets reporting, but official confirmation pending</li>
      <li>Official statement + satellite imagery with minor discrepancies</li>
      <li>Multiple social media reports from credible sources corroborating</li>
    </ul>
    <p><strong>Color/Badge:</strong> <span class="badge likely">Likely</span></p>
  </div>

  <div class="confidence-level unconfirmed">
    <h4>? Unconfirmed</h4>
    <p>
      <strong>Requirement:</strong> Single source OR claims without independent verification.
      May be accurate but needs confirmation before higher classification.
    </p>
    <p><strong>Examples:</strong></p>
    <ul>
      <li>Claim by one news outlet, waiting for official confirmation</li>
      <li>Eyewitness account without independent verification</li>
      <li>Casualty estimates (often have high variance)</li>
    </ul>
    <p><strong>Color/Badge:</strong> <span class="badge unconfirmed">Unconfirmed</span></p>
  </div>

  <div class="confidence-level disproven">
    <h4>✗ Disproven</h4>
    <p>
      <strong>Requirement:</strong> Claim contradicted by credible evidence or multiple authoritative sources.
      Initially reported but now known to be false.
    </p>
    <p><strong>Examples:</strong></p>
    <ul>
      <li>Report retracted by originating news outlet</li>
      <li>Official denial with supporting evidence</li>
      <li>Claim contradicted by satellite imagery or independent verification</li>
    </ul>
    <p><strong>Color/Badge:</strong> <span class="badge disproven">Disproven</span></p>
  </div>
</div>
```

---

## 7. Editorial & Sourcing Policy Outline

This is the full text for your `/methodology/` page. Publish this verbatim.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>How We Report: Editorial Methodology | Epic Fury Live</title>
  <meta name="description" content="Our editorial standards, source verification system, and commitment to accuracy in conflict reporting.">
  <link rel="canonical" href="https://epicfurylive.com/methodology/">
</head>

<body>

<article class="methodology-page">

<h1>How We Report: Editorial Methodology</h1>

<p class="tagline">
  Epic Fury Live is committed to accurate, transparent, and ethically reported conflict information.
  This page documents our editorial standards and source verification system.
</p>

---

## Our Mission

Epic Fury Live is a free, volunteer-run, ad-free public service tracker of the 2026 US-Israel-Iran conflict.
We aim to provide:

1. **Verified incident reporting** — Only facts we can confirm from reliable sources
2. **Transparent uncertainty** — Clear labeling of what we know vs. don't know
3. **Public trust** — No sensationalism, no speculation, no hidden funding
4. **Correction accountability** — Public log of every error we make and how we fixed it

---

## Source Tier System

We classify all sources using a three-tier system, from most to least reliable:

### Tier 1: Official & Primary Sources

**Definition:** Direct statements from governments, militaries, official organizations, or primary witnesses.

**Examples:**
- Official statements from US Department of Defense, Israeli Defense Forces, Iranian government
- UN Security Council statements
- International Committee of the Red Cross (ICRC) field reports
- Satellite imagery with official metadata (MAXAR, commercial providers)
- Academic research from peer-reviewed sources
- Primary government data (casualty counts from official sources)

**How we use Tier 1:**
- **Single Tier 1 source + one other source** = Likely to Confirmed status
- **Two independent Tier 1 sources** = Confirmed status
- We wait for Tier 1 confirmation before marking major incidents as "Confirmed"

---

### Tier 2: Major Credible Outlets

**Definition:** Established news organizations with journalistic standards, editorial oversight, and track record of accuracy.

**Examples:**
- Reuters, Associated Press, Bloomberg, BBC, NPR, The Guardian, The Wall Street Journal, Financial Times
- Major international outlets (Al Jazeera, France24, Deutsche Welle, etc.)
- Established regional outlets with editorial standards
- Defense/military analysis from Jane's Intelligence Review, SIPRI, Center for Strategic Studies

**How we use Tier 2:**
- **3+ independent Tier 2 sources** = Confirmed status (if Tier 1 unavailable)
- **2 Tier 2 sources** = Likely status
- **Single Tier 2 source** = We wait or mark as Unconfirmed

**Exclusions:**
- Opinion sections (even from major outlets)
- Analysis without fact-checking
- Outlets known for spreading unverified claims

---

### Tier 3: Unverified / Social Media

**Definition:** Eyewitness accounts, unverified claims, social media reports, analysis without independent verification.

**Examples:**
- Eyewitness videos from civilians (no independent verification)
- Twitter/X posts from anonymous accounts
- Unverified claims from advocacy groups
- "According to social media reports" without verification
- Anonymous military sources without attribution

**How we use Tier 3:**
- We do NOT mark incidents as Confirmed based on Tier 3 alone
- We may report Tier 3 information with **Unconfirmed** status
- Tier 3 can support Tier 1/2 claims but cannot stand alone
- We clearly label Tier 3 as "unverified" or "reports suggest"

**What we WON'T publish from Tier 3:**
- Casualty figures (too prone to exaggeration)
- Unverified military capabilities claims
- Allegations without cross-source verification

---

## Incident Verification Process

Here's exactly how we verify an incident before publishing:

### Step 1: Initial Report (Real-time)
- Incident reported by 1+ source (any tier)
- We immediately publish as **Unconfirmed**
- Clearly labeled: "Reports suggest..." "Alleged..." "Claim requires verification"

### Step 2: Seek Tier 1 Confirmation (First 1-2 hours)
- Contact/monitor official sources (government statements, military briefings)
- Check for satellite imagery with metadata
- Monitor Tier 2 outlets for follow-up reporting

### Step 3: Cross-Reference (2-6 hours)
- If Tier 1 available: Move to **Confirmed** with Tier 1 citation
- If only Tier 2 available: Wait for 3+ independent outlets OR seek Tier 1
- If strong disagreement between sources: Label as "disputed"

### Step 4: Final Classification
- **Confirmed** = Tier 1 + 1 other source, OR 3+ Tier 2 independent sources
- **Likely** = 2 credible sources with minor inconsistencies
- **Unconfirmed** = Single source or awaiting verification
- **Disproven** = Evidence contradicts original claim

### Step 5: Updates
- If new information changes status, we update and note the change
- Never silently correct without logging
- All corrections go to `/corrections/` page with timestamp

---

## Casualty Reporting: Special Standards

Casualty figures are highly prone to exaggeration, speculation, and error. We apply stricter standards:

**What we report:**
- Official government casualty figures (with source attribution)
- Casualty figures from Tier 2 outlets citing Tier 1 sources
- ICRC/UN casualty assessments where available
- Population impact from credible organizations (Doctors Without Borders, etc.)

**What we label as Unconfirmed:**
- Estimates from analysis or modeling
- Social media casualty claims
- Any figure not from official or major outlet sources

**What we don't publish:**
- "According to social media, X people died" (unverified)
- Wild estimates with no sourcing
- Predictions about future casualties

**Example:**
- ✅ "Iran reports 5 military casualties (official IRNA statement)"
- ❌ "Estimated 50-100 casualties (unverified reports)"
- ✅ "Humanitarian impact reports suggest 2,000+ displaced (ICRC, verified)" (with source link)

---

## No Sensationalism Pledge

We commit to:

1. **Avoid inflammatory language**
   - "Airstrike" not "barbaric attack"
   - "Military response" not "retaliation" (too loaded)
   - Facts, not adjectives

2. **Avoid speculation**
   - Not: "Iran is planning a revenge attack..."
   - Yes: "Historical patterns suggest Iran may respond in 24-72 hours"
   - Source claims when speculating

3. **Avoid clickbait titles**
   - Not: "SHOCKING: Drone Strike DESTROYS Facility!"
   - Yes: "Airstrike Confirmed: Isfahan Facility Damaged"

4. **Avoid conflict amplification**
   - Not: "This proves war is inevitable"
   - Yes: "This incident raises escalation concerns. De-escalation channels remain open."

5. **Avoid dehumanization**
   - Always refer to people as people, not numbers
   - Include human context where appropriate
   - Casualties and displacement matter

---

## Uncertainty Labeling

When we don't know something, we say so:

**Examples of proper uncertainty language:**
- "Damage assessment is ongoing; initial reports suggest..." (prefix with status)
- "Casualty figures remain unconfirmed" (be explicit)
- "Iranian claims 40% facility damage; satellite imagery analysis pending" (show disagreement)
- "Current assessment: Likely 2-3 aircraft involved, but confirmation needed" (show confidence level)

**What we avoid:**
- Silent omission (don't just skip unknown info)
- Hedging without clarity ("may have possibly..." is vague)
- Presenting estimates as facts

---

## Analysis vs. Reporting

We separate fact from analysis:

### Reporting (Fact-Based)
- "3 airstrikes confirmed on March 5"
- "Reuters reports Iran claims 2 casualties"
- "Satellite imagery shows facility 60% damaged"

### Analysis (Labeled as such)
- "**Analysis:** This targets Iran's drone production capacity, potentially limiting future operations"
- "**Assessment:** Historical precedent suggests 24-72 hour window for response"
- "**Strategic significance:** This incident may accelerate UN diplomatic efforts"

**We clearly label analysis** with bolded headers so readers know it's interpretation, not fact.

---

## Corrections & Accountability

We make mistakes. Here's how we handle them:

1. **When we discover an error:**
   - Correct the original page immediately
   - Add an update note: "CORRECTION: [original claim]. Updated [timestamp] because [reason]."
   - Log in `/corrections/` with full details

2. **What goes in corrections log:**
   - Original claim (quote)
   - What was wrong
   - Corrected information
   - Why we got it wrong (source retracted, misread, later clarification, etc.)
   - Timestamp

3. **Example correction:**
   ```
   March 5, 14:32 UTC Report: "5 casualties reported in Isfahan airstrike"
   Correction (March 5, 18:00 UTC): Iran later stated 0-2 casualties.
   We published the initial report before confirmation. Lesson: Await casualty confirmation.
   ```

4. **Public corrections page**
   - All corrections logged and searchable
   - Buildable trust through transparency

---

## Conflicts of Interest & Funding

**Who we are:**
- Epic Fury Live is a volunteer-run, non-profit project
- No corporate or government funding
- Ad-free by design
- Open source code and data

**Our transparency:**
- No hidden funding sources
- Volunteers are from diverse backgrounds (conflict researchers, journalists, technologists, humanitarians)
- We disclose any conflicts explicitly

**Financial support:**
- Donation-supported (paypal, crypto, etc. details TBD)
- No expectation of editorial control from donors
- Donors cannot request edits or kills

---

## Special Topics: Verification Standards

### Casualty Claims
- Official sources only, or major outlets citing officials
- Always marked Unconfirmed unless from Tier 1
- Include confidence level

### Cyber Attacks
- Attribution requires 2+ credible sources
- Never speculate on attribution without evidence
- Cite cybersecurity researchers by name when possible

### Chemical/Nuclear Incidents
- Extreme caution; wait for Tier 1 confirmation
- Official denial ≠ proof of absence
- Link to OPCW, IAEA statements where relevant

### Disinformation Debunks
- Only debunk claims that have gained traction
- Cite original claim and evidence against it
- Don't amplify conspiracy theories

---

## Contact & Feedback

- **Editorial questions:** [email protected]
- **Corrections/tips:** [corrections@epicfurylive.com]
- **Source submissions:** [sources@epicfurylive.com]

We review all feedback and corrections seriously.

---

## Version & Updates

**Last updated:** March 5, 2026
**Version:** 1.0

This methodology may be updated as we learn and as the conflict evolves.
All significant changes will be noted here with dates.

</article>

</body>
</html>
```

---

## 8. 14-Day Publishing Plan

Sustainable daily/weekly publishing for a 1-2 person team:

### Daily (5 min - 30 min)

**Morning routine (if time permits, optional):**
- Check official statements (US DoD, IDF, Iran IRNA)
- Scan Reuters, AP, Al Jazeera for overnight incidents
- If major incident: add to `/updates/` with **Unconfirmed** label

**Afternoon routine (required):**
- Check for Tier 1 confirmation of any overnight incidents
- Update confidence levels if new sources available
- Add to `/updates/` feed (1-3 new items typical)
- Track incident in `/incidents/` database
- Update home page "Last updated" timestamp

**Evening routine (60-90 min, creates tomorrow's content):**
- Compile today's incidents
- Write `/briefs/YYYY-MM-DD/` summary (5-7 incidents typical)
- Publish daily brief with links to related incidents, actors, glossary
- Update `/sitemap.xml` lastmod date
- Push to GitHub Pages

**Realistic effort:** 30-90 min per day, depending on incident volume.

---

### Weekly (2-3 hours)

**Every Monday:**
- Review `/corrections/` log for the past week
- Review any unconfirmed incidents for updates
- Verify casualty figures if available
- Update `/incidents/?type=` filters/search

**Every Wednesday:**
- Audit `/actors/` pages for currency
- Update actor involvement statistics (# incidents, # days involved)
- Add new actor pages if new groups involved

**Every Friday:**
- Comprehensive timeline audit
- Check for gaps or missed incidents
- Update glossary with new terms that week's incident reporting required
- Publish `/corrections/` page summary if any corrections made

---

### Avoid Thin Content

**What NOT to do:**
- ❌ Create `/briefs/` with < 2 incidents (combine with previous day)
- ❌ Publish incident pages with < 50 words of description
- ❌ Add actor pages for minor figures (wait until 3+ incidents involve them)
- ❌ Create glossary terms for concepts mentioned once

**Minimum content standards:**
- Daily brief: 2+ incidents, 3+ sources, 300+ words
- Incident page: 2+ sources, incident details, timeline, analysis (500+ words)
- Actor page: 3+ incidents, role context, relationships to other actors (400+ words)
- Glossary term: Definition, context, related terms, 1+ example from incidents (200+ words)

**If low on content:**
- Better to publish nothing than thin filler
- Update home page with "Updates in progress" message
- Catch up when incident volume higher

---

### Realistic Scenario: Average Week

**Monday:** 4 airstrikes reported
- 4 new `/incidents/` pages (1.5 hrs creating + linking)
- 1 daily brief (45 min)
- Update actors involved (30 min)
- Total: 2.5-3 hours

**Tuesday:** 1 diplomatic statement
- Add to daily brief (15 min)
- Link from related incidents (10 min)
- Total: 25 min

**Wednesday:** 2 cyber incidents
- 2 incident pages (1 hour)
- 1 daily brief (45 min)
- Update glossary (cyber warfare terms) (30 min)
- Total: 2.25 hours

**Thursday-Sunday:** Lower activity
- Daily briefs if incidents (30 min each)
- Corrections/updates only
- Review/verify pending items
- Weekly maintenance (Friday)

**Weekly total:** 6-8 hours for 1-2 person team
**Realistic:** 1 person spending 1 hour/day + weekend catch-up

---

## 9. Launch Checklist (30-60 minutes)

Execute these steps once, during launch weekend:

### Step 1: Google Search Console Setup (10 minutes)

1. Go to https://search.google.com/search-console
2. Click **Add Property**
3. Enter: `https://epicfurylive.com`
4. Choose **URL prefix** (easier than domain verification for GitHub Pages)
5. Verify ownership via HTML file:
   - Download verification HTML file from Google
   - Add to root of GitHub Pages repo as `/google-site-verification-[code].html`
   - Push to GitHub
   - Confirm in Search Console
6. Click **Go to property**

### Step 2: Submit Sitemap (5 minutes)

1. In Search Console, go to **Sitemaps**
2. Click **Add/test sitemaps**
3. Enter: `https://epicfurylive.com/sitemap.xml`
4. Click **Submit**
5. Google will crawl it within 24 hours

### Step 3: Request URL Indexing (5 minutes)

1. In Search Console, click **URL inspection** (top search bar)
2. Enter: `https://epicfurylive.com/`
3. Click **Request indexing**
4. Repeat for key pages:
   - `/briefs/`
   - `/incidents/`
   - `/methodology/`
   - `/actors/`
   - `/glossary/`

### Step 4: Set Up Analytics (Non-Invasive) (10 minutes)

**Use Plausible Analytics or Fathom (privacy-first, no cookie consent needed):**

1. Sign up at https://plausible.io (14-day free trial)
2. Add your domain: `epicfurylive.com`
3. Add tracking code to `<head>` of all pages:
   ```html
   <script defer data-domain="epicfurylive.com" src="https://plausible.io/js/script.js"></script>
   ```
4. Test: Visit your site, check Plausible dashboard (updates in real-time)

**Alternative (free):** Use Goatcounter (fully self-hosted, zero tracking)
```html
<script data-goatcounter="https://epicfurylive.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
```

### Step 5: Submit RSS Feed (5 minutes)

**Existing RSS aggregators (build upon launch):**

1. Google News: https://news.google.com/news/sitemap/news-publishers
   - Add sitemap.xml with news elements
   - Wait 1-2 weeks for Google News inclusion

2. Feedburner/Feedly:
   - Submit `/rss.xml` to https://feedly.com/i/discover/sources/search/epicfurylive
   - Users can subscribe directly

3. Major directories:
   - Submit to journalist newsletter platforms (Substack, LinkedIn)
   - Add RSS badge to home page

---

### Step 6: Backlink Starter Actions (10 minutes)

**Day 1 — Launch outreach:**

1. **Twitter/X announcement**
   - Post launch announcement
   - Tag @Reuters, @AP, @JanesMIL, @ConflictNews
   - Use hashtags: #IranIsraelConflict #Tracking #WarTracker

2. **Journalist communities**
   - Post in r/journalism (Reddit): "New free war tracker launched"
   - Post in IRE (Investigative Reporters & Editors) groups
   - Post in Data Journalism communities

3. **Conflict research communities**
   - Post in conflict/security studies forums
   - Link on academic conflict databases
   - Reach out to think tanks (IISS, CSIS, etc.) with press release

4. **Newsletter directories**
   - Add to Substack/Medium network if on those platforms
   - Submit to newsletter aggregators

5. **Initial backlink targets (do via email):**
   - Journalists covering the conflict (send press release)
   - NGOs focused on humanitarian tracking (ICRC, Médecins Sans Frontières)
   - University conflict studies departments
   - Think tanks (Carnegie, Wilson Center, etc.)

---

### Step 7: Enable GitHub Pages Custom Domain (Already Done)

- Confirm `epicfurylive.com` is set in GitHub Pages settings
- Verify DNS records point to GitHub (should already be configured)
- Enable HTTPS (GitHub handles automatically)

---

## 10. Done Definition — Success Metrics

Track these in Google Search Console. Set targets for month 1, 2, 3:

### Indexed Pages Target

| Milestone | Target | Timeline |
|-----------|--------|----------|
| **Launch** | 15+ pages indexed (home, briefs, incidents, methodology, glossary, etc.) | Day 1 |
| **Month 1** | 50+ pages (daily briefs + incident pages) | Week 2-4 |
| **Month 2** | 100+ pages | Week 5-8 |
| **Month 3** | 150+ pages | Week 9-12 |

**Track in:** Google Search Console > Coverage > Indexed pages

---

### Click-Through Rate (CTR) Targets

Healthy CTR for informational/news content is 2-5% (clicks per 100 impressions).

| Milestone | Target | Timeline |
|-----------|--------|----------|
| **Month 1** | 1-2% CTR (new site, low impressions expected) | Week 1-4 |
| **Month 2** | 2-3% CTR (as content grows, improve rankings) | Week 5-8 |
| **Month 3** | 3-5% CTR (targeting top-10 keywords improves CTR) | Week 9-12 |

**Note:** CTR varies by query intent. Brand searches will be 5-15%. Informational searches 1-3%.

**Track in:** Google Search Console > Performance > Click-through rate

---

### Position Targets (Keyword Rankings)

Target these keyword clusters and track in Search Console:

| Keyword Cluster | Target Position | Timeline | Example Queries |
|-----------------|-----------------|----------|-----------------|
| "Live updates" queries | Top 10 | Month 1-2 | "live updates iran israel conflict" |
| "Timeline" queries | Top 10 | Month 2-3 | "iran israel conflict timeline 2026" |
| "Map" queries | Top 5 | Month 2-3 | "conflict map iran israel 2026" |
| "What happened today" | Top 10 | Month 1 | "what happened iran israel today" |
| "Confirmed reports" | Top 5 | Month 2 | "confirmed reports iran israel conflict" |
| Brand (epicfurylive) | #1 | Immediate | "epicfurylive", "epic fury live" |

**Track in:** Google Search Console > Performance > click on each query, check "average position"

---

### AI Citation Tracking Approach

AI search engines (Perplexity, Claude.com, Gemini) cite sources when they're well-structured. Track indirectly:

**Method 1: Manual Monitoring**
- Search Perplexity: "US Israel Iran conflict updates March 2026"
- Look for "cited from epicfurylive.com" in results
- Screenshot and log

**Method 2: Analytics Referral Tracking**
- Set up UTM parameters for AI engine referrals
- When linking to your site, AI engines don't always show up in referrers
- Look for unexplained traffic spikes to `/methodology/` or `/incidents/` (sign of AI scraping)

**Method 3: Google Search Results**
- If you rank top-5, Google will show you in AI snapshots
- AI tools cite top-ranking sources
- This is visible in Google Search Console as "impressions" (see if CTR drops; AI might be answering without clicks)

**Target:** By month 3, you should appear in at least 1-2 AI search result summaries per day for target queries.

---

### Monthly Impression & Traffic Targets

| Month | Target Impressions | Target Clicks | Target Sessions | Target Pages/Session |
|-------|-------------------|---------------|-----------------|----------------------|
| **Month 1** | 5K | 100-150 | 80-120 | 1.5-2 |
| **Month 2** | 20K | 400-600 | 300-400 | 1.8-2.2 |
| **Month 3** | 50K+ | 1.5K-2.5K | 1K-1.5K | 2-2.5 |

**Impressions** = search results your site appears in
**Clicks** = actual visits from search
**Sessions** = unique visitors
**Pages/Session** = how much users explore once they visit

**Track in:** Google Search Console > Performance overview

---

### Content Completeness Audit

By end of month 1, you should have:

- ✅ 20+ `/incidents/` pages (with sources, timeline, analysis)
- ✅ 20+ `/briefs/` (daily summaries)
- ✅ 10+ `/actors/` pages (key countries and groups)
- ✅ 50+ `/glossary/` terms (defined military/political terms)
- ✅ 1 `/corrections/` page (public corrections log)
- ✅ 1 `/methodology/` page (editorial standards)
- ✅ 1 `/map/` page (interactive)
- ✅ RSS feed auto-updating

---

### Ranking Position Distribution

By month 3, aim for:

- **20%** of tracked keywords in top 3 positions
- **40%** of tracked keywords in top 10 positions
- **70%** of tracked keywords in top 30 positions

Example:
- 50 tracked keywords
- 10 in top 3
- 20 in top 10
- 35 in top 30

---

### Bounce Rate Target

Target: **40-50% bounce rate** for a news/tracker site (healthy range)

- Below 30% = users exploring deeply (good but rare for news)
- 40-50% = healthy (users find answer and leave, or explore 1-2 pages)
- Above 70% = poor UX or off-topic traffic

**Track in:** Google Analytics (Plausible or Google Analytics 4)

---

### Authority/Backlink Targets

By end of month 3, aim for:

- **50+** referring domains (sites linking to you)
- **100+** total backlinks
- Average Domain Authority of referring sites: 40+

**Track with:** Ahrefs, Semrush, or free Moz Link Explorer

---

### Search Console Health Checks

**Monthly checklist:**

1. **Crawl Stats** — Ensure consistent crawl activity (Google visiting your site daily)
2. **Core Web Vitals** — Keep LCP < 2.5s, FID < 100ms, CLS < 0.1
3. **Coverage** — No increase in errors; all valid pages indexed
4. **Security Issues** — Zero malware/hacking alerts
5. **Manual Actions** — Should be none (if present, site is penalized)
6. **Keyword Performance** — Track top 50 keywords for position/CTR trends

---

## Final Notes for Implementation

### Quick Start (Day 1)

1. Create `/sitemap.xml` in repo root
2. Create `/robots.txt` in repo root
3. Add all Open Graph + Twitter meta tags to `index.html`
4. Add all JSON-LD structured data to `index.html`
5. Add favicon + webmanifest
6. Push to GitHub Pages
7. Complete Google Search Console setup (10 min)
8. Submit sitemap
9. Request indexing of home page

### Week 1

1. Build site structure (create `/briefs/`, `/incidents/`, `/actors/`, `/glossary/`, `/methodology/`)
2. Write `/methodology/` page in full
3. Create 5-10 `/incidents/` pages from major recent events
4. Create 2-3 `/actors/` pages (USA, Iran, Israel minimum)
5. Create 20+ `/glossary/` entries
6. Set up analytics (Plausible or Fathom)
7. Create `/corrections/` page template

### Week 2

1. Create daily `/briefs/` pages (7 total for launch week)
2. Link incidents, actors, glossary throughout
3. Create `/updates/` feed template and start populating
4. Launch `/map/` page
5. Set up RSS feed
6. Outreach to journalists, researchers, communities

### Month 1+

1. Publish `/briefs/` daily
2. Add `/incidents/` as major incidents occur
3. Weekly actor/glossary updates
4. Monthly methodology reviews
5. Weekly backlink/PR outreach

---

## File Checklist for Repo

Ensure these files exist in your GitHub Pages repo:

```
epicfurylive.com/ (GitHub Pages repo root)
├── index.html (home page with all structured data)
├── robots.txt
├── sitemap.xml
├── rss.xml
├── atom.xml
├── favicon.ico
├── site.webmanifest
├── 404.html
├── /assets/
│   ├── og-image-1200x630.png
│   ├── twitter-card-1024x512.png
│   ├── logo-600x400.png
│   ├── icon-192.png
│   ├── icon-512.png
│   └── [incident images, maps, etc.]
├── /briefs/
│   ├── index.html
│   ├── 2026-03-05/
│   │   └── index.html
│   ├── 2026-03-04/
│   │   └── index.html
│   └── [daily folders]
├── /incidents/
│   ├── index.html (searchable list)
│   ├── isfahan-shahed-march-5/
│   │   └── index.html
│   ├── tactical-base-march-5/
│   │   └── index.html
│   └── [incident folders]
├── /actors/
│   ├── index.html
│   ├── usa/
│   │   └── index.html
│   ├── iran/
│   │   └── index.html
│   ├── israel/
│   │   └── index.html
│   └── [actor folders]
├── /glossary/
│   └── index.html (all terms on single page with anchors)
├── /methodology/
│   └── index.html
├── /corrections/
│   └── index.html
├── /map/
│   └── index.html
└── /css/
    └── styles.css
```

---

## Summary

This plan provides:

1. **Technical SEO** — robots.txt, sitemap, structured data, metadata
2. **Information architecture** — URL patterns, site structure, content templates
3. **Content templates** — Copy-paste HTML for incidents, briefs, methodology
4. **Editorial standards** — Full methodology page text
5. **Publishing workflow** — Realistic 14-day plan for small team
6. **Launch checklist** — 30-60 minute setup
7. **Success metrics** — Measurable targets for Google Search, CTR, rankings, AI citations

**The goal:** Become the go-to source for verified conflict tracking, cited by Google Search, AI models, journalists, and researchers within 3 months of launch.

