# Security & Ethical/Legal Scope

## Ethical/Legal Boundaries (project guide §26)

This project operates strictly on publicly available information. It does
**not**:

- access restricted systems or bypass authentication
- circumvent access controls or scrape sites against their published terms
- collect credentials of any kind
- conduct surveillance of private individuals
- exploit software vulnerabilities
- target private individuals unnecessarily — entities of interest should be
  public figures, organizations, or entities already discussed in public
  source material

## Security Principles (project guide §25)

Applied incrementally as phases add the relevant component:

| Principle | Applies starting | Notes |
|---|---|---|
| Input validation | Phase 1 | All connector output validated before normalization |
| API authentication | Phase 6 | FastAPI endpoints behind auth once a real UI consumes them |
| Rate limiting | Phase 1 (outbound), Phase 6 (inbound) | Be a well-behaved client of public APIs; protect the API once exposed |
| Secrets management | Phase 1 | `.env`, never committed; see `.env.example` |
| Dependency scanning | Phase 1+ | `pip-audit` / GitHub Dependabot in CI |
| Database permissions | Phase 2 | Least-privilege DB roles for app vs. migrations |
| Audit logging | Phase 4 | Entity-resolution decisions logged (see `data-model.md` `ResolutionDecision`) |
| Container security | Phase 1 | Non-root Docker users, pinned base images |
| Malicious document content | Phase 1 | Treat all fetched content as untrusted input — no `eval`, sanitize before storage/display |

## Data Minimization

The system should avoid collecting sensitive personal information beyond
what's already public and relevant to the entities/events being modeled.
Attributes like private contact details, biometric data, or anything not
present in the public source material are out of scope.
