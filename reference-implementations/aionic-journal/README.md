# Aionic Journal — SAFE Reference Implementation

A privacy-first journal demonstrating SAFE session consent.

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:5173

## What This Demonstrates

1. **Session consent** — SAFE screen on every session start, lists data streams
2. **Permission granularity** — each stream authorized separately
3. **Expiry** — all permissions gone when tab closes; next session asks again
4. **Zero retention default** — "No, local only" keeps the app fully functional

## Architecture

```
src/
  continuity/
    rings.js      — Three-ring storage (Source / Continuity / Bridge)
    coherence.js  — Entry coherence scoring (CI)
    deltaE.js     — ΔE entropy field calculations
  App.jsx         — Consent screen + journal UI
  App.css         — Dark warm theme
  main.jsx        — React entry point
```

## Data Streams

| Stream | Required | Notes |
|--------|----------|-------|
| Journal entries | No | App works without consent — no persistence |
| Export to file | No | Download entries as JSON |

## ΔE Tracking

Every save computes a coherence index (CI) against recent entries.
ΔE = rate of change in CI over time. Badge in header shows state:

- `↑ ΔE+` regenerative — coherence increasing
- `· ΔE=` stable — no significant change
- `↓ ΔE−` decaying — coherence drifting

## Notes

In-memory storage only — data lost on refresh. Intentional for a reference implementation.
Production use: replace `Map()` in rings.js with Dexie IndexedDB calls.

ΔΣ=42
