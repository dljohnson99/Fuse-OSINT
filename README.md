# Fuse OSINT

Open-Source Intelligence Fusion & Analysis Platform.

Fuse OSINT ingests heterogeneous public information (news, government data),
normalizes it into a common data model, extracts entities/events/relationships,
resolves duplicate entities across sources, and represents the result as a
time-aware, evidence-traceable knowledge graph that an analyst can search,
visualize, and investigate.

> Every relationship the system asserts must be traceable back to the source
> evidence that produced it. Uncertainty is represented explicitly, not hidden.

This is an independent/student research project. It uses only public, legally
accessible data. See [`docs/security.md`](docs/security.md) for the ethical
and legal boundaries the project operates within.

## Status

**Phase 0 — Research & Architecture** (see [`docs/architecture.md`](docs/architecture.md))

## Project Phases

| Phase | Focus | Status |
|---|---|---|
| 0 | Research & Architecture | 🔵 In progress |
| 1 | Data Ingestion MVP | ⬜ Not started |
| 2 | Common Data Model | ⬜ Not started |
| 3 | NLP Extraction | ⬜ Not started |
| 4 | Entity Resolution | ⬜ Not started |
| 5 | Knowledge Graph | ⬜ Not started |
| 6 | Analyst Interface | ⬜ Not started |
| 7 | Investigation Workspace | ⬜ Not started |
| 8 | Evaluation | ⬜ Not started |

## Quickstart (target — not yet functional)

```bash
git clone <repo>
cd osint-fusion-platform
docker compose up -d
python ingestion/run.py --source news_rss
python intelligence/run_pipeline.py
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — system architecture & data flow
- [`docs/data-model.md`](docs/data-model.md) — canonical Entity/Document/Event/Relationship model
- [`docs/ontology.md`](docs/ontology.md) — entity types, relationship types, event types
- [`docs/sources.md`](docs/sources.md) — Phase 1 source definitions
- [`docs/ingestion.md`](docs/ingestion.md) — connector interface
- [`docs/entity-resolution.md`](docs/entity-resolution.md) — matching approach
- [`docs/evaluation.md`](docs/evaluation.md) — metrics & test methodology
- [`docs/security.md`](docs/security.md) — security & ethical/legal scope

## Tech Stack

Python (FastAPI) · PostgreSQL · Neo4j · React/TypeScript · spaCy/transformers · Docker

## License

TBD (recommend MIT or Apache-2.0 for a portfolio project).
