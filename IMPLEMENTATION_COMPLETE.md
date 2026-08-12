# Implementation Scope and Remaining Gates

The accepted implementation is the deterministic evidence path under
`backend/rca_evidence/` and `backend/evidence_app.py`.

## Implemented and Measured

- Bounded STDF v4-subset binary ingestion
- 75 reproducible synthetic files and 30-document corpus
- Six measured LangGraph agent nodes
- BM25 retrieval and evidence fusion
- Validation-only candidate selection
- Sealed 25-case confirmation
- Citation/groundedness/report/safety metrics
- Engineer-review routing
- SQLite persistence and stage traces
- Authenticated upload and report API
- Responsive local workbench
- Hash-verified serving identity
- Non-root minimal Linux image definition
- 23 focused tests, strict lint, data regeneration, and claim replay
- Removal of vulnerable mocked backend and unused React dependency surfaces

## Not Complete

- Real-domain STDF compatibility and expert-adjudicated accuracy
- External LLM evaluation
- Production identity/RBAC and high-availability persistence
- Load, soak, disaster-recovery, and uptime evidence
- Linux container execution on the local Windows-only engine
- Remote CI and anonymous post-publication verification

This file records scope; it is not a production-readiness declaration.
