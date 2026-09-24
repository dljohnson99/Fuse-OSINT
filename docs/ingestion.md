# Ingestion Connector Interface

Every source connector implements the same interface (project guide §8) so
new sources can be added without touching the rest of the pipeline. See
`ingestion/connectors/base.py` for the actual abstract base class.

```
fetch()      -> raw payload(s) from the source (network call or file read)
parse()      -> structured-but-source-specific records from the raw payload
validate()   -> drops/flags malformed records before they're normalized
normalize()  -> maps source-specific fields to the canonical Document/Entity shape
store()      -> writes RawRecord (unmodified) + normalized Document to PostgreSQL
```

## Contract

- `fetch()` must be idempotent-safe: re-running it should not create
  duplicate `RawRecord`s (dedupe via `content_hash`).
- `parse()` should raise a typed error on unexpected schema changes rather
  than silently dropping fields — Phase 1 success criteria requires
  ingesting "without manual database entry," which means failures need to
  be visible, not silent.
- `validate()` runs before `normalize()`; a record that fails validation is
  logged with a reason and excluded from normalization, not discarded
  silently.
- `store()` always writes the raw payload first (§9, Raw Data Layer),
  even if normalization later fails — raw preservation must not depend on
  downstream success.

## Adding a New Connector

1. Create `ingestion/connectors/<source_name>.py` implementing
   `BaseConnector`.
2. Add a normalization mapping in `ingestion/normalization/<source_name>.py`
   (see `data-model.md` normalization example).
3. Register the connector in `ingestion/connectors/registry.py`.
4. Add a fixture + unit test under `tests/ingestion/` using a saved sample
   response (don't hit the live network in tests).
