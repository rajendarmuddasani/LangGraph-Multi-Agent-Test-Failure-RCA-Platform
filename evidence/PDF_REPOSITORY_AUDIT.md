# Project 08 Repository Audit

Last audited: 2026-08-11
Repository: LangGraph-Multi-Agent-Test-Failure-RCA-Platform
Base commit: `0a79f73fa804aa26ea130ebd07165b25dfdd6bd4`

## Audit Outcome

The original repository contained a six-agent architecture, but its STDF, RAG,
hypothesis, service, and deployment evidence was mocked or externally dependent.
The old Python manifest had 129 known vulnerabilities, and the unused React
production dependency set had seven. Those surfaces and their stale guides were
removed rather than presented as completed work.

The accepted replacement is one deterministic six-node LangGraph 1.2.10 path
with real bounded STDF parsing, local BM25 retrieval, SQLite persistence,
validation-only policy selection, sealed confirmation, cited reports, a
hash-bound FastAPI runtime, and a hardened Chainguard image definition.

## Accepted Reproduced Claims

| Claim | Evidence |
|---|---|
| 75 independently generated STDF files, 10,800 die, 75,600 measurements | `data/synthetic_rca_v1/manifest.json` |
| 30/20/25 development/validation/confirmation split | split manifests and data card |
| 30-document real local BM25 corpus | `data/synthetic_rca_v1/corpus.json` |
| Four frozen validation candidates | `evidence/candidate_results.json` |
| `fusion_balanced_v1` selected before confirmation opened | `evidence/selection.json` |
| Six real LangGraph 1.2.10 nodes and traces | `backend/rca_evidence/workflow.py`, focused tests |
| 25/25 synthetic confirmation causes, macro F1 1.000 | `evidence/model_evaluation.json` |
| Accuracy Wilson 95% interval 86.68% to 100% | `evidence/model_evaluation.json` |
| 72% automatic coverage at 100% accepted accuracy | `evidence/model_evaluation.json` |
| 100% groundedness/citation correctness; 0% unsupported/hallucination | `evidence/model_evaluation.json` |
| 4.05/5.34/5.46 ms local p50/p95/p99 | `evidence/model_evaluation.json` |
| Zero external LLM calls and $0.00 API cost | `evidence/runtime_manifest.json` |
| Four of four corrupt inputs rejected | `evidence/model_evaluation.json` |
| 23 focused tests and 91% accepted-runtime coverage | `evidence/local_validation.json` |
| No known accepted dependency CVEs; zero Bandit findings | `evidence/local_validation.json` |
| Desktop/mobile runtime and private docs without overflow | `evidence/local_validation.json` |

## Candidate Decisions

| Candidate | Validation accuracy | Coverage | Evidence sources | p95 | Decision |
|---|---:|---:|---:|---:|---|
| `rules_v1` | 95% | 95% | 2.90 | 4.67 ms | Rejected; one reviewed error |
| `retrieval_v1` | 100% | 95% | 1.00 | 4.57 ms | Rejected; single-source path |
| `fusion_balanced_v1` | 100% | 95% | 3.95 | 4.23 ms | Selected |
| `fusion_retrieval_heavy_v1` | 100% | 95% | 3.95 | 5.17 ms | No improvement; slower |

## Rejected Historical Claims

| Historical claim | Class | Reason |
|---|---|---|
| 4-8 hours reduced to 20-30 minutes | target | No controlled before/after timing study |
| Greater than 85% real expert-match accuracy | unsupported | No licensed real corpus or expert adjudication |
| 500 or more RCAs/day and production uptime | unsupported | No load, soak, or operations telemetry |
| Production-ready/autonomous RCA | unsupported | No real-domain, authority, or operations approval |
| Savings, yield, or escape impact | unsupported | No accepted business or material-outcome evidence |

## Truth Boundary

- Independent synthetic benchmark only.
- Bounded STDF v4 subset, not universal STDF compatibility.
- The perfect 25-case result has an 86.68% Wilson lower bound.
- Confirmation contained no error, so review recall has denominator zero.
- Local latency is not a production SLO.
- The selected policy uses no external LLM.
- The Linux image cannot run on the local Windows-container daemon; its build and
  runtime smoke remain a pending remote CI gate.

## Reproduction

```powershell
python -m pytest -q --cov=rca_evidence --cov=evidence_app
python -m ruff check backend/rca_evidence backend/evidence_app.py scripts tests --select E,W,F --ignore E501
python scripts/validate_evidence.py
python scripts/run_evidence_benchmark.py --stage replay
python -m pip_audit -r backend/requirements-evidence.txt --progress-spinner off
python -m bandit -r backend/rca_evidence backend/evidence_app.py -q
```

No commit, push, profile update, resume update, or other remote write is included
in this local audit.
