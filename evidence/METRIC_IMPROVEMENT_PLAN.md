# Project 08 Metric Improvement Plan

Last updated: 2026-08-11
Status: synthetic evidence phase complete; real-domain promotion deferred

## Completed Objective

Move Project 08 from architecture-first claims to a reproducible synthetic RCA
benchmark with real ingestion, retrieval, six-node LangGraph sessions,
persistence, safety routing, and canonical evidence.

## Frozen Selection Protocol

Candidates:

1. `rules_v1`: statistical/spatial/correlation rules only
2. `retrieval_v1`: BM25 knowledge retrieval only
3. `fusion_balanced_v1`: 70% rules + 30% retrieval with evidence gate
4. `fusion_retrieval_heavy_v1`: 45% rules + 55% retrieval with evidence gate

Selection score:

`0.40*task_success + 0.25*cause_accuracy + 0.20*citation_correctness + 0.15*groundedness`

Safety gates:

- task success at least 98%;
- report quality at least 95%;
- hallucination at most 5%;
- unsupported citations at most 2%;
- review recall at least 95% when errors exist;
- fail-closed behavior for invalid evidence/input.

Eligible ties were broken by cause accuracy, evidence-source diversity, lower
local p95, then lexical policy ID. Confirmation remained unopened until
`selection.json` recorded `fusion_balanced_v1` and the confirmation-manifest
SHA-256.

## Completed Result

- Validation: 20 cases; selected balanced fusion at 100% cause accuracy,
  95% automatic coverage, 3.95 mean evidence-source diversity, and 4.23 ms p95.
- Confirmation: 25 cases; 25/25 causes correct, 1.000 macro F1, 86.68% to 100%
  Wilson interval, 72% automatic coverage, 100% accepted accuracy.
- Evidence/report safety: 100% groundedness and citation correctness, 0%
  unsupported citations and hallucination under repository definitions.
- Runtime: six LangGraph 1.2.10 nodes, SQLite persistence, authenticated FastAPI,
  responsive workbench, hash-bound policy/evaluation/corpus identity.
- Software: 23 focused tests, 91% coverage, strict lint, no known accepted
  dependency CVEs, zero Bandit findings, deterministic 80-file regeneration.

## Weakest Accepted Behavior

The confirmation set contains only 25 independently generated synthetic cases
and no incorrect prediction. Therefore:

- the 100% point estimate must be paired with its 86.68% Wilson lower bound;
- confirmation review recall is undefined as empirical error capture because its
  error denominator is zero;
- 28% review routing is a workload measure, not proof of real safety;
- no real-domain generalization is accepted.

## Next Experiment Phase

Do not reopen the current confirmation set for selection. Build a new licensed or
independently generated challenge line with:

1. malformed and uncommon STDF record combinations for parser fuzzing;
2. unseen geometry, signal, and mixed-cause scenarios;
3. explicit no-answer and insufficient-evidence cases;
4. product/tester/lot/time-like group isolation;
5. label noise and expert disagreement representation;
6. enough errors to estimate review recall and calibration;
7. load/concurrency, soak, persistence recovery, and bounded resource tests.

Potential challengers:

- calibrated balanced fusion with explicit abstention probability;
- BM25 plus a current local embedding model, selected on new validation only;
- bounded LLM synthesis with structured output, citation enforcement, safety,
  latency, cost, and memorization testing;
- parallel LangGraph analysis branches if they improve measured p95 without
  weakening deterministic trace order or failure isolation.

## Real-Domain Promotion Gate

Require all of the following before any operational claim:

- licensed representative STDF and documented provenance;
- expert-adjudicated root causes with disagreement handling;
- product/tester/lot/time isolation;
- confidence calibration and review policy with nonzero error denominator;
- parser fuzzing and security review;
- load, soak, outage/recovery, and resource envelope;
- production identity, RBAC, persistence, observability, and approval;
- a newly sealed confirmation set opened once after selection.
