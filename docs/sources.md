# Data Sources — Phase 1 Definitions

Per project guide §7/§23, the MVP targets **two** source types so the
normalization layer proves it can reconcile genuinely different schemas.

## Source 1: News / RSS (unstructured, Category A)

- **Connector name:** `news_rss`
- **Access method:** Public RSS/Atom feeds from established outlets
  (e.g. Reuters, AP, a regional outlet's public feed). No scraping behind
  paywalls or logins.
- **Fields available:** title, article text, author (often absent),
  publish date, URL.
- **What we extract:** People, Organizations, Locations, Events mentioned
  in the body text via NLP (Phase 3) — this source has *no* structured
  entity fields, so it exercises the extraction pipeline.
- **Update cadence:** Poll on a schedule (e.g. every 30–60 min); dedupe by
  `content_hash` of the article body.

## Source 2: Government Data (structured, Category B)

- **Connector name:** `gov_contracts` (recommended starting dataset:
  USAspending.gov award data, or a state procurement portal's public CSV/API
  — both are public, reproducible, and rate-limit friendly)
- **Access method:** Public API or bulk CSV download.
- **Fields available (example — USAspending award record):** recipient
  name, award amount, award date, awarding agency, place of performance.
- **What we extract:** These fields map close to 1:1 onto
  `Organization`/`Location`/`Relationship(contracted_with-equivalent)` —
  this source exercises the *normalization* layer rather than NLP, since
  the fields are already structured. See `data-model.md` §"Normalization
  Layer" example (Source A `company_name`/`award_value`/`award_date` vs.
  Source B `recipient`/`amount`/`date`).

## Why This Pair

- One unstructured + one structured source forces the normalization layer
  to actually reconcile different schemas (project guide §10), rather than
  ingesting two similar feeds that don't test fusion.
- Both are freely accessible without authentication, satisfying the
  reproducibility principle (§6.5) and the ethical/legal scope (§26) —
  no restricted systems, no credentials, no scraping behind auth walls.

## Deferred Sources (Phase 5+)

- Corporate filings (Category C) — e.g. SEC EDGAR full-text search API.
- Geospatial (Category D) — e.g. OpenStreetMap/Nominatim for geocoding
  Location entities once the Geographic View (project guide §17 View 5) is
  built.
- Historical/research datasets (Category E) — useful as a fixed,
  known-ground-truth set for entity-resolution evaluation (Phase 8).

## Explicitly Out of Scope

Per project guide §26: no restricted systems, no bypassing authentication,
no credential collection, no scraping sites that prohibit it in their
terms of service or robots.txt, no targeting private individuals who
aren't otherwise public figures in the source material.
