# Evaluation

Per project guide §22 Phase 8 and §27. The goal is to replace "it seems to
work" with measured numbers.

## Ground Truth Dataset

- ~100 documents (mixed news + government records) manually annotated with:
  - entities (with correct type)
  - relationships (subject, predicate, object)
  - events
- Stored under `evaluation/datasets/`, versioned, never silently edited
  (annotation changes go through a dated snapshot).

## Metrics

| Component | Metrics |
|---|---|
| Entity extraction | Precision, Recall, F1 (per entity type) |
| Entity resolution | True/False positives & negatives, Precision, Recall |
| Relationship extraction | Precision, Recall, F1 |
| System performance | Ingestion throughput, query latency, graph traversal time, processing time/document |
| Analyst utility (qualitative) | Time to locate relevant evidence, # sources needed, # manually-identified relationships vs. system-found |

## Test Levels

- **Unit tests** (`tests/`): parsers, normalization functions, matching
  functions, DB operations, API endpoints — run against fixtures, not live
  network calls.
- **Integration tests**: full source → ingestion → normalization → NLP →
  database → graph path, run against a small fixed fixture set.
- **Data quality tests**: missing fields, invalid timestamps, duplicate
  records, malformed entities/relationships caught before graph write.

## Reporting

Results land in `evaluation/results/` as dated reports (metrics table +
short narrative of what changed since the last run), feeding the final
technical report (project guide §42, deliverable 9).
