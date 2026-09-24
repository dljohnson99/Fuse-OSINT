# Entity Resolution Approach

## Problem

Different sources refer to the same real-world entity with different
strings ("Alpha Technologies" / "Alpha Tech" / "ATI"). Entity resolution
decides when two mentions should be merged into one canonical `Entity`.

## Phase 4 Approach (MVP)

1. **Candidate generation** — for a new mention, retrieve existing entities
   with similar names (e.g. blocking on first token + trigram/edit-distance
   threshold) rather than comparing against every entity in the database.
2. **Feature scoring** — compute per project guide §13:
   - name similarity (e.g. Jaro-Winkler or embedding cosine similarity)
   - location overlap
   - shared associated people/organizations (context similarity)
   - identifier match (if both records have e.g. a ticker or registry ID)
   - temporal consistency (do the mentions' timeframes conflict?)
3. **Score combination** — start with a simple weighted sum for
   interpretability; revisit as a learned classifier only if the
   labeled evaluation set (Phase 8) shows the simple model underperforming.
4. **Threshold routing** — per `ontology.md` confidence bands:
   - ≥ 0.90 → auto-merge
   - 0.70–0.89 → write as `pending` in `ResolutionDecision`, surface in UI
     for analyst confirm/reject (project guide §6.4, §17 example)
   - < 0.70 → keep as separate entities

## What Gets Logged

Every resolution attempt — merged or not — is written to
`resolution_decisions` (see `data-model.md`) so the process is auditable
and can be scored against ground truth in Phase 8.

## Evaluation

See `evaluation.md`. Entity resolution is scored with true/false
positives/negatives, precision, and recall against a manually labeled set
of known-duplicate and known-distinct entity pairs.
