# Canonical Data Model

This defines the common representation every source is normalized into,
before any NLP or resolution happens. See `ontology.md` for the controlled
vocabularies (entity types, relationship predicates, event types) referenced
here.

## RawRecord (pre-normalization, PostgreSQL `raw_records`)

| Field | Type | Notes |
|---|---|---|
| id | UUID | PK |
| source_id | text | connector identifier, e.g. `news_rss:reuters` |
| source_type | enum | `news` \| `government` \| `corporate` \| `geospatial` \| `dataset` |
| source_url | text | original URL, nullable for bulk datasets |
| retrieved_at | timestamptz | when Fuse fetched it |
| published_at | timestamptz | nullable — source may not provide this |
| raw_content | text/bytea | unmodified payload |
| content_hash | text | sha256, used for dedup |

## Document (PostgreSQL `documents`)

```
Document
├── id                UUID
├── raw_record_id      FK → RawRecord
├── source             text
├── title              text
├── author             text (nullable)
├── published_date     date (nullable)
├── retrieved_date     date
├── text               text (cleaned/extracted body)
└── url                text
```

## Entity (PostgreSQL `entities`, mirrored as nodes in Neo4j)

```
Entity
├── id                UUID
├── type              EntityType (see ontology.md)
├── canonical_name     text
├── aliases[]          text[]
├── attributes         jsonb   -- type-specific, e.g. {"dob": ..., "hq_location": ...}
└── confidence         float [0,1]   -- confidence this entity node is well-formed/resolved
```

## Relationship (PostgreSQL `relationships`, mirrored as edges in Neo4j)

```
Relationship
├── id                UUID
├── subject_id         FK → Entity
├── predicate          RelationshipType (see ontology.md)
├── object_id          FK → Entity
├── confidence         float [0,1]
├── start_date         date (nullable)
├── end_date           date (nullable)
├── evidence[]          Evidence[]
└── contradicting_evidence[]  Evidence[]  -- sources that dispute this relationship
```

## Event (PostgreSQL `events`, mirrored in Neo4j)

```
Event
├── id                UUID
├── type              EventType (see ontology.md)
├── timestamp          timestamptz (nullable — may be date-only or range)
├── location_id         FK → Entity (type=Location, nullable)
├── participants[]       FK[] → Entity
└── evidence[]           Evidence[]
```

## Evidence (PostgreSQL `evidence`)

```
Evidence
├── id                UUID
├── document_id         FK → Document
├── span_start / span_end   int (nullable) -- character offsets of the supporting text
├── extraction_method    text  -- e.g. "spacy_ner", "manual", "rule_pattern"
└── extracted_at         timestamptz
```

Every `Relationship` and `Event` MUST have at least one `Evidence` row before
it is written to Neo4j. This is enforced in the Validation Layer, not left
to convention — see `architecture.md` §5 and project guide §6.2.

## Entity Resolution Audit (PostgreSQL `resolution_decisions`)

Tracks how two entity mentions were merged or kept separate, so resolution
is itself auditable:

```
ResolutionDecision
├── id                UUID
├── mention_a_id        text  -- raw extracted mention, pre-resolution
├── mention_b_id        text
├── resolved_entity_id   FK → Entity (nullable if rejected)
├── match_score          float
├── features             jsonb  -- {"name_similarity": 0.94, "location_match": 1.0, ...}
├── decision             enum  -- auto_merged | human_confirmed | human_rejected | pending
└── decided_at            timestamptz
```

## Neo4j Graph Mirror

- Nodes: `Entity` (labeled by `type`, e.g. `:Person`, `:Organization`)
- Edges: `Relationship`, typed by `predicate`, carrying `confidence`,
  `start_date`, `end_date`, and an `evidence_ids` property (list of UUIDs
  pointing back to PostgreSQL `evidence` rows — full evidence text is never
  duplicated into the graph).
