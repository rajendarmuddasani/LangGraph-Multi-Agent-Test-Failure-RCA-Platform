# Changelog

All notable accepted-runtime changes are documented here. Historical mocked
service claims are intentionally excluded because they were not reproducible
evidence.

## [Unreleased] - 2026-08-11

### Added

- 75-file independently generated synthetic STDF benchmark
- Disjoint 30/20/25 development, validation, and confirmation manifests
- Bounded STDF v4-subset parser and deterministic generator
- Six-node LangGraph 1.2.10 RCA workflow
- Statistical, spatial, and correlation analysis
- Real local BM25 retrieval over 30 versioned documents
- Four frozen candidate policies and validation-only selection
- Sealed 25-case confirmation with finite-sample uncertainty
- Groundedness, citation, report, review, latency, cost, and recovery metrics
- SQLite session and stage-trace persistence
- API-key FastAPI runtime and responsive report workbench
- Hash-bound policy/evaluation/corpus startup verification
- Hardened Chainguard non-root image and Compose controls
- Deterministic evidence regeneration and confirmation replay
- Public data, policy, deployment, security, and claim cards

### Changed

- Replaced the vulnerable mocked LangChain/OpenAI/Qdrant/PostgreSQL scaffold with
  the evaluated local LangGraph path.
- Replaced the unused vulnerable React scaffold with the accepted static
  workbench served by FastAPI.
- Reconciled public documentation to synthetic-only evidence boundaries.

### Removed

- Legacy dependency manifest with 129 known vulnerabilities
- Legacy frontend production dependencies with seven known vulnerabilities
- Placeholder service credentials and product/tester-specific planning text
- Unsupported production-ready, throughput, uptime, time-savings, and accuracy
  claims

### Validation

- Full focused tests, strict Ruff lint, deterministic data regeneration,
  confirmation replay, pip-audit, Bandit, browser desktop/mobile checks, and
  privacy/provenance scans are required before publication approval.
