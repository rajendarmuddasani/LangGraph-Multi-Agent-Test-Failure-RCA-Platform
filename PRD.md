# Product Requirements: Evidence-Backed Synthetic STDF RCA

Status: locally implemented and validated on independent synthetic evidence
Version: 1.0
Last updated: 2026-08-11

## Purpose

Provide a reproducible reference workflow that accepts a bounded STDF v4 subset,
executes six traceable analysis stages, retrieves relevant synthetic RCA evidence,
ranks one root-cause class, routes uncertainty to engineer review, persists the
complete trace, and produces a cited report.

This specification does not define a production ATE controller or claim
performance on real semiconductor data.

## Users

- Validation engineer reviewing a synthetic RCA workflow
- Software engineer reproducing parser, retrieval, and policy evidence
- Reviewer auditing claim-to-artifact consistency and failure behavior

## Functional Requirements

### Input and Parsing

- Accept `.stdf` multipart uploads up to 8 MiB.
- Parse FAR, MIR, WIR, PIR, PTR, PRR, WRR, and MRR records.
- Reject wrong version/endianness, malformed records, incomplete lifecycle,
  duplicate tests/coordinates, nonfinite results, and configured resource-limit
  violations.
- Record input SHA-256, lot/wafer identity, record counts, die count, failures,
  yield, and test names.

### Six-Stage Workflow

1. Data Analyst: validated input summary
2. Statistical Analyst: failed/pass standardized effects
3. Spatial Pattern Detector: edge, stripe, cluster, and entropy features
4. Correlation Hunter: measurement-to-failure correlations
5. Conclusion Engine: BM25 retrieval and deterministic score fusion
6. Report Generator: ranked hypotheses, citations, limitations, and next steps

Every completed session must contain all six ordered stage traces and latencies.

### Retrieval and Evidence

- Index a versioned 30-document synthetic knowledge corpus with local BM25.
- Build retrieval queries only from observed analysis signals.
- Resolve each report citation to an evidence-registry entry.
- Mark material claims unsupported when no supporting citation exists.

### Selection and Review

- Compare the four predeclared policies on validation only.
- Select using the frozen weighted objective and safety gates.
- Keep confirmation unopened until selection records its manifest hash.
- Require review below the configured confidence threshold, on rule/retrieval
  disagreement, or when source diversity is insufficient.

### Persistence and API

- Persist complete result JSON and normalized stage traces in SQLite.
- Require `X-API-Key` for analysis, session, and report routes.
- Provide health, public manifest, versioned sample, analysis, sessions, and HTML
  report endpoints.
- Provide a responsive workbench for sample loading and evidence inspection.

### Integrity and Deployment

- Fail startup when policy, evaluation, or corpus identity differs from the
  runtime manifest.
- Provide a minimal Chainguard non-root image.
- Use a read-only root filesystem, dropped capabilities, no-new-privileges, and
  one explicit persistence volume in Compose.

## Evidence Requirements

- Independent synthetic provenance and MIT license
- Disjoint development, validation, and confirmation groups
- Retained rejected and no-improvement candidates
- Cause accuracy, macro F1, per-class metrics, finite-sample uncertainty
- Task success, report quality, groundedness, citation correctness
- Unsupported-citation and hallucination rates
- Automatic coverage, accepted accuracy, and review routing
- Local p50/p95/p99 latency, external-call count, and API cost
- Corrupt-input recovery and deterministic replay

## Non-Functional Requirements

- Python 3.10 through 3.12 test matrix
- Deterministic regeneration of every committed benchmark file
- Strict Ruff E/W/F lint on the accepted surface
- No known CVEs in accepted runtime Python dependencies
- No internal identifiers, credentials, or production data in public files
- Desktop and 390 px mobile layouts without horizontal overflow

## Explicit Non-Goals

- Real-domain RCA accuracy
- Universal STDF compatibility
- Automated material disposition
- Production throughput, uptime, or service-level objectives
- Business savings, yield improvement, or cycle-time claims
- External LLM quality claims
- Kubernetes or enterprise identity claims

## Promotion Gates

A real-domain release requires licensed representative STDF, expert-adjudicated
labels, product/tester/lot/time isolation, calibrated uncertainty, parser fuzzing,
load/soak and outage/recovery tests, production identity and persistence, and
independent operating approval.
