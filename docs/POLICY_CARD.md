# Policy Card: Fusion Balanced v1

## Intended Decision

Rank one synthetic root-cause class, attach traceable evidence, and route
uncertain or rule/retrieval-disagreement cases to engineer review. The policy
cannot disposition material or control test equipment.

## Candidate Selection

Four candidates were frozen before validation:

| Candidate | Rule / retrieval weight | Validation accuracy | Automatic coverage | Evidence sources | Local p95 |
|---|---:|---:|---:|---:|---:|
| `rules_v1` | 100 / 0 | 95% | 95% | 2.90 | 4.67 ms |
| `retrieval_v1` | 0 / 100 | 100% | 95% | 1.00 | 4.57 ms |
| `fusion_balanced_v1` | 70 / 30 | 100% | 95% | 3.95 | 4.23 ms |
| `fusion_retrieval_heavy_v1` | 45 / 55 | 100% | 95% | 3.95 | 5.17 ms |

Selection objective:

`0.40*task_success + 0.25*cause_accuracy + 0.20*citation_correctness + 0.15*groundedness`

The balanced fusion policy won the frozen tie-break on evidence diversity and
lower p95 latency. The rules-only candidate's one validation error was routed
to review. All candidate results, including non-selected trials, remain in
`evidence/candidate_results.json`.

## Confirmation Result

| Metric | Accepted result |
|---|---:|
| Cases | 25 (5 per class) |
| Cause accuracy / macro F1 | 100% / 1.000 |
| Accuracy 95% Wilson interval | 86.68% to 100% |
| Task success | 100% |
| Automatic coverage | 72% |
| Accuracy among automatically accepted cases | 100% |
| Engineer-review routing | 28% |
| Groundedness / citation correctness | 100% / 100% |
| Unsupported citation / hallucination rate | 0% / 0% |
| Report quality | 100% |
| Local latency p50 / p95 / p99 | 4.05 / 5.34 / 5.46 ms |
| External LLM calls / API cost | 0 / $0.00 |
| Corrupt-input rejection | 4/4 |

No confirmation case was incorrect, so review recall has denominator zero. It
must not be described as demonstrated error capture on confirmation; development
and validation errors were all routed to review.

## Metric Definitions

- **Task success:** completed output, six stage traces, and all report sections.
- **Groundedness:** fraction of material claims with at least one valid supporting
  citation.
- **Citation correctness:** citations that resolve and support the associated
  root-cause or spatial claim.
- **Report quality:** required report sections present and nonempty.
- **Hallucination:** material claim without a valid supporting citation.
- **Automatic coverage:** cases not routed to engineer review.

## Runtime Identity

- Runtime ID: `synthetic-rca-evidence-v1`
- Selected policy: `fusion_balanced_v1`
- Evaluation SHA-256:
  `3551e661d57843f47e9ebbb97fd85c8bf96d66630abbd3eb9077f870559d1c31`

The API verifies this identity and the corpus hash at startup and fails closed
on drift.

## Remaining Gates

Real-domain promotion requires licensed representative STDF, expert-adjudicated
root causes, product/tester/lot/time isolation, calibrated uncertainty, a larger
challenge set with actual errors, load/soak evidence, and operating approval.
