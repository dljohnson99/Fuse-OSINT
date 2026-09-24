# Architecture

## 1. Pipeline Overview

```
Public Sources (News/RSS, Government)
        │
        ▼
Ingestion Service  (per-source connectors: fetch → parse → validate → normalize → store)
        │
        ▼
Raw Data Store     (immutable, content-hashed, retrieval metadata preserved)
        │
        ▼
Normalization      (source-specific schema → canonical Document/Entity records)
        │
        ▼
NLP Pipeline       (NER, date/location extraction, relationship & event extraction)
        │
        ▼
Entity Resolution  (candidate generation → scoring → auto-resolve or human review)
        │
        ▼
Relationship / Event Construction
        │
        ▼
Validation Layer   (schema checks, confidence thresholds, contradiction detection)
        │
        ├──────────────┬───────────────┐
        ▼              ▼
   PostgreSQL        Neo4j
   (documents,       (entities, relationships,
    entities,         graph traversal)
    audit log)
        └──────────────┴───────────────┘
                    │
                    ▼
                FastAPI  (/search /entities /relationships /events /documents)
                    │
                    ▼
            React/TypeScript UI (search, entity profile, graph, timeline, map, evidence)
                    │
                    ▼
                 Analyst
```

## 2. Why Two Databases

- **PostgreSQL** is the system of record for documents, raw metadata, source
  provenance, and audit history — anything relational and write-heavy.
- **Neo4j** holds the derived graph (entities + relationships) for traversal
  queries ("what connects to what, within N hops") that are awkward in SQL.
- Every graph node/edge in Neo4j carries a foreign key back to the
  PostgreSQL evidence records that justify it — the graph is never the sole
  source of truth for *why* a fact exists.

## 3. Component Responsibilities

| Component | Responsibility | Owns |
|---|---|---|
| Ingestion Service | Pull raw data from a source on a schedule/trigger | `ingestion/connectors/*` |
| Raw Data Store | Preserve retrieved content unmodified, deduplicated by content hash | `/raw` on disk (Phase 1), object storage later |
| Normalization | Map source-specific fields to the canonical model | `ingestion/normalization/*` |
| NLP Pipeline | Extract entities, dates, locations, relationships, events from text | `intelligence/extraction/*` |
| Entity Resolution | Decide whether two entity mentions are the same real-world entity | `intelligence/entity_resolution/*` |
| Relationship/Event Builder | Assemble extracted spans into typed graph-ready records | `intelligence/relationships/*`, `intelligence/events/*` |
| Validation Layer | Reject malformed records; flag low-confidence/contradictory ones for review | `backend/services/validation.py` |
| API | Expose search/query/investigation endpoints | `backend/api/*` |
| UI | Search, entity profile, graph, timeline, map, evidence views | `frontend/*` |

## 4. Data Flow Contract Between Stages

Each stage consumes and produces well-defined objects (see `data-model.md`):

- Ingestion → Raw Data Store: `RawRecord` (source_id, source_type, source_url, retrieved_at, published_at, raw_content, content_hash)
- Normalization → NLP: `Document`
- NLP → Entity Resolution: `CandidateEntity[]`, `CandidateRelationship[]`, `CandidateEvent[]`
- Entity Resolution → Graph: `ResolvedEntity` (with confidence + alias set)
- Graph Builder → Storage: `Entity`, `Relationship`, `Event` (each with `Evidence[]`)

## 5. Confidence & Evidence Propagation

Confidence is computed at each stage that introduces uncertainty (NER
confidence, extraction confidence, entity-resolution match score) and
combined — not overwritten — as a record moves downstream. The final
`Relationship.confidence` and its full evidence list (including any
*contradictory* evidence) must always be queryable from the UI's Evidence
View (see final project guide, §16, §17 View 6).

## 6. Phase 1 Scope Boundary

Phase 1 (Data Ingestion MVP) implements exactly one connector end-to-end
through raw storage, to validate the interface in §8 of the project guide
before generalizing to multiple sources. See `docs/sources.md`.

## 7. Deferred / Not in Scope for MVP

- Natural-language query layer (§19 of project guide) — structured
  graph/SQL queries only until Phase 6+ is stable.
- Predictive/anomaly modeling (§37) — explicitly out of scope until the
  factual fusion pipeline is proven.
- Real-time/streaming ingestion — batch/scheduled pulls only.
