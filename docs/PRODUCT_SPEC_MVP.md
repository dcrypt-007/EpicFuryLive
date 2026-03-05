# EpicFuryLive — MVP Spec

## Purpose
Public OSINT dashboard for conflict events, claims verification, and polling trends.

## Core Principle
Claims are not facts. Everything is attribution-first and source-linked.

## Objects
- Claim (UNVERIFIED -> CONFIRMED/DISPROVEN)
- VerifiedEvent (normalized, citation-backed)
- Poll (region sentiment; not all questions comparable)

## Default UX
Home = map-first.
Default view shows VerifiedEvents only; Claims excluded from totals unless toggled.

## Safety / Scope
No tactical tracking. No precise coordinates beyond city/province level by default.
