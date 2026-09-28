# Ontology

Controlled vocabularies for `data-model.md`. Deliberately small for the MVP —
extend only when a real source requires it (see project guide §23, item 1:
"ingest public data from at least two source types" before broadening).

## Entity Types (MVP)

| Type | Description | Example attributes |
|---|---|---|
| `Person` | A named individual | `role`, `dob`, `bioguide_id`, `party`, `state` (if public) |
| `Organization` | Company, agency, nonprofit | `hq_location`, `industry` |
| `Location` | City, region, address, coordinate | `lat`, `lon`, `admin_level` |
| `Event` | A discrete occurrence (also see Event model) | `event_type` |
| `Document` | Source document, not a graph "subject" entity but resolvable/searchable | — |

Deferred to later phases: `Facility`, `Vehicle` (§11 of project guide lists
these — add once a source actually supplies them; don't model speculatively).

A 'Document' can be a United States Congress Bill. It is a document with a stable ###-XX-#### form (congress, type, number), plus attributes for congress, bill type, and bill number. A 'Person' has expanded attributes to include those of Bill Sponsors.

## Relationship Types (MVP)

| Predicate | Subject type | Object type | Meaning |
|---|---|---|---|
| `works_for` | Person | Organization | employment / affiliation |
| `located_at` | Organization \| Person | Location | physical presence |
| `attended` | Person | Event | participation |
| `mentioned_in` | Entity (any) | Document | co-occurrence / citation |
| `sponsored` | Person | Document | primary sponsor of bill |

Deferred: `owns`, `founded`, `acquired`, `contracted_with` — add in Phase 3
once the NLP pipeline needs them for a real source, per project guide §12.

## Event Types (MVP)

| Type | Description |
|---|---|
| `contract_awarded` | Government/corporate contract announcement |
| `appointment` | Person appointed to a role/organization |
| `organization_founded` | Organization formation |

## Naming & Alias Conventions

- `canonical_name` is the form the system displays and resolves toward.
- All other observed name forms go into `aliases[]` — never silently
  discarded (this is what makes "Alpha Tech" → "Alpha Technologies Inc."
  auditable rather than a black box, per project guide §6.4).

## Confidence Bands (used for UI display and auto-resolve thresholds)

| Band | Range | Behavior |
|---|---|---|
| High | ≥ 0.90 | Auto-resolved / displayed without warning |
| Medium | 0.70–0.89 | Flagged for human confirmation before graph write |
| Low | < 0.70 | Kept as candidate only; not written to Neo4j |

These thresholds are a starting point — Phase 4/8 evaluation should revisit
them against labeled data, not treat them as fixed.
