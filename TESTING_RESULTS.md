# Testing Results

Last local validation: 2026-08-11
Base before this work: `0a79f73fa804aa26ea130ebd07165b25dfdd6bd4`

## Automated Tests

```text
23 passed, 0 failed
```

The suite covers the accepted parser, deterministic generation, split isolation,
BM25 retrieval, six-node LangGraph workflow,
metrics, candidate selection, SQLite persistence, authenticated API, report,
upload bounds, and runtime tamper detection.

Combined statement coverage for `rca_evidence` and `evidence_app` is 91%.

One warning remains from the installed Starlette/httpx TestClient compatibility
notice. It does not affect pass/fail status and is not presented as resolved.

## Strict Lint

```text
All checks passed!
```

Scope: `backend/rca_evidence`, `backend/evidence_app.py`, evaluation scripts,
and their focused tests using Ruff E/W/F rules.

## Security and Privacy

- `pip-audit`: zero known vulnerabilities in the four accepted dependencies
- Bandit: zero findings on the accepted Python runtime
- Workspace diagnostics: zero errors after switching to Chainguard images
- Public privacy scan: zero secret or restricted-identifier matches
- Compose configuration: parses successfully

## Deterministic Evidence

```text
status: pass
files compared: 80
STDF files compared: 75
runtime manifest SHA-256:
e2764c53ad4f09446a4919693c7a556ac9ff6a326513d01511746ade7bd09ac1
model evaluation SHA-256:
3551e661d57843f47e9ebbb97fd85c8bf96d66630abbd3eb9077f870559d1c31
corpus SHA-256:
cb98093f0e6ba1231e33923b3b12af367f064b74e0b9097fd5e69f09691bdbb1
```

All 75 files were regenerated in a temporary directory and matched byte for
byte. Frozen confirmation replay matched every stable claimed metric.

## Confirmation

| Metric | Result |
|---|---:|
| Cases / classes | 25 / 5 |
| Cause accuracy / macro F1 | 100% / 1.000 |
| Accuracy Wilson 95% interval | 86.68% to 100% |
| Automatic coverage / accepted accuracy | 72% / 100% |
| Review rate | 28% |
| Groundedness / citation correctness | 100% / 100% |
| Hallucination / unsupported citations | 0% / 0% |
| Report quality / task success | 100% / 100% |
| Local p50 / p95 / p99 | 4.05 / 5.34 / 5.46 ms |
| External calls / cost | 0 / $0.00 |
| Corrupt inputs rejected | 4/4 |

## Browser

The private one-page and public runtime UI are validated separately at desktop
and 390 px mobile widths. Browser results and screenshots remain private under
`pdocs/` and are excluded from the public payload.

## Container

The Linux container definition is complete and CI contains build, readiness,
authenticated STDF analysis, and non-root checks. Local execution is blocked by
the workstation's Windows-only Docker daemon; a successful Linux container run
must not be claimed until remote CI passes after publication.

## Truth Boundary

These results describe a finite independent synthetic benchmark and local
software behavior. They do not establish performance on real STDF or production
operations.
