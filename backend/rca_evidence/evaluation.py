"""Candidate evaluation, safety gates, and confirmation evidence metrics."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .analysis import ROOT_CAUSES
from .synthetic import GENERATOR_VERSION
from .workflow import POLICIES, RCAEvidenceWorkflow


REQUIRED_REPORT_KEYS = (
    "title",
    "executive_summary",
    "input",
    "findings",
    "ranked_hypotheses",
    "citations",
    "review_required",
    "limitations",
    "next_steps",
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def write_json(path: Path, value: Any) -> str:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(quantile * len(ordered)) - 1)
    return float(ordered[index])


def _classification_metrics(
    expected: Sequence[str],
    predicted: Sequence[str],
) -> Dict[str, Any]:
    per_class: dict[str, dict[str, float | int]] = {}
    f1_values: list[float] = []
    for root_cause in ROOT_CAUSES:
        true_positive = sum(
            expected_value == root_cause and predicted_value == root_cause
            for expected_value, predicted_value in zip(expected, predicted)
        )
        false_positive = sum(
            expected_value != root_cause and predicted_value == root_cause
            for expected_value, predicted_value in zip(expected, predicted)
        )
        false_negative = sum(
            expected_value == root_cause and predicted_value != root_cause
            for expected_value, predicted_value in zip(expected, predicted)
        )
        support = sum(value == root_cause for value in expected)
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        f1_score = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        f1_values.append(f1_score)
        per_class[root_cause] = {
            "precision": precision,
            "recall": recall,
            "f1": f1_score,
            "support": support,
        }
    accuracy = sum(
        expected_value == predicted_value
        for expected_value, predicted_value in zip(expected, predicted)
    ) / len(expected)
    return {
        "accuracy": accuracy,
        "macro_f1": statistics.fmean(f1_values),
        "per_class": per_class,
    }


def _bootstrap_accuracy_interval(
    expected: Sequence[str],
    predicted: Sequence[str],
    *,
    seed: int = 8_081,
    iterations: int = 2_000,
) -> Dict[str, float]:
    # Deterministic bootstrap sampling, not a security boundary.
    random_source = random.Random(seed)  # nosec B311
    sample_count = len(expected)
    values: list[float] = []
    for _ in range(iterations):
        correct = 0
        for _sample_index in range(sample_count):
            index = random_source.randrange(sample_count)
            correct += expected[index] == predicted[index]
        values.append(correct / sample_count)
    values.sort()
    return {
        "lower_95": values[int(0.025 * (iterations - 1))],
        "upper_95": values[int(0.975 * (iterations - 1))],
        "iterations": iterations,
        "seed": seed,
    }


def wilson_accuracy_interval(
    successes: int,
    total: int,
    *,
    z_score: float = 1.959963984540054,
) -> Dict[str, float | int]:
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("Wilson interval requires 0 <= successes <= total")
    proportion = successes / total
    denominator = 1.0 + z_score**2 / total
    center = (proportion + z_score**2 / (2 * total)) / denominator
    half_width = (
        z_score
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z_score**2 / (4 * total**2)
        )
        / denominator
    )
    return {
        "lower_95": 0.0 if successes == 0 else max(0.0, center - half_width),
        "upper_95": 1.0 if successes == total else min(1.0, center + half_width),
        "successes": successes,
        "total": total,
    }


def _citation_metrics(result: Mapping[str, Any]) -> Dict[str, float | int]:
    registry = result["evidence_registry"]
    material_claims = result["report"]["material_claims"]
    correct_citations = 0
    total_citations = 0
    grounded_claims = 0

    for claim in material_claims:
        claim_text = str(claim["claim"])
        claim_correct = 0
        for citation_id in claim.get("citations", []):
            total_citations += 1
            evidence = registry.get(citation_id)
            if evidence is None:
                continue
            if claim_text.startswith("Primary root cause:"):
                predicted_root_cause = result["prediction"]["root_cause"]
                is_correct = predicted_root_cause in evidence.get("supports", [])
            elif claim_text.startswith("Spatial pattern:"):
                expected_suffix = claim_text.split(":", 1)[1].strip()
                is_correct = citation_id == f"analysis:spatial#{expected_suffix}"
            else:
                is_correct = True
            if is_correct:
                correct_citations += 1
                claim_correct += 1
        if claim_correct > 0:
            grounded_claims += 1

    claim_count = len(material_claims)
    return {
        "citation_correctness": (
            correct_citations / total_citations if total_citations else 0.0
        ),
        "groundedness": grounded_claims / claim_count if claim_count else 0.0,
        "unsupported_citation_rate": (
            (total_citations - correct_citations) / total_citations
            if total_citations
            else 1.0
        ),
        "hallucination_rate": (
            (claim_count - grounded_claims) / claim_count if claim_count else 1.0
        ),
        "citation_count": total_citations,
        "material_claim_count": claim_count,
    }


def score_case(result: Mapping[str, Any], expected_root_cause: str) -> Dict[str, Any]:
    traces = result["stage_traces"]
    task_success = (
        result["status"] == "completed"
        and len(traces) == 6
        and all(result["report"].get(key) is not None for key in REQUIRED_REPORT_KEYS)
    )
    present_sections = sum(
        bool(result["report"].get(key))
        or isinstance(result["report"].get(key), bool)
        for key in REQUIRED_REPORT_KEYS
    )
    citations = _citation_metrics(result)
    predicted_root_cause = result["prediction"]["root_cause"]
    return {
        "task_success": float(task_success),
        "correct": predicted_root_cause == expected_root_cause,
        "expected_root_cause": expected_root_cause,
        "predicted_root_cause": predicted_root_cause,
        "confidence": result["prediction"]["confidence"],
        "review_required": bool(result["review_required"]),
        "report_quality": present_sections / len(REQUIRED_REPORT_KEYS),
        "evidence_source_diversity": len(
            result["prediction"]["evidence_source_types"]
        ),
        "latency_ms": result["latency_ms"],
        "external_llm_calls": result["external_llm_calls"],
        "external_cost_usd": result["external_cost_usd"],
        **citations,
    }


def evaluate_policy(
    data_root: Path,
    split_manifest: Mapping[str, Any],
    corpus: Sequence[Mapping[str, Any]],
    policy_id: str,
) -> Dict[str, Any]:
    if policy_id not in POLICIES:
        raise ValueError(f"Unknown candidate: {policy_id}")
    workflow = RCAEvidenceWorkflow(corpus, policy_id)
    case_scores: list[dict[str, Any]] = []
    sample_result: dict[str, Any] | None = None

    for case in split_manifest["cases"]:
        payload = (data_root / case["relative_path"]).read_bytes()
        payload_hash = hashlib.sha256(payload).hexdigest()
        if payload_hash != case["file_sha256"]:
            raise ValueError(f"Case hash mismatch: {case['case_id']}")
        workflow_result = workflow.analyze(
            payload,
            session_id=f"{policy_id}-{case['case_id']}",
        )
        result_dict = workflow_result.to_dict()
        score = score_case(result_dict, case["expected_root_cause"])
        score.update(
            {
                "case_id": case["case_id"],
                "group_id": case["group_id"],
                "ambiguous": case["ambiguous"],
                "input_sha256": case["file_sha256"],
            }
        )
        case_scores.append(score)
        if sample_result is None:
            sample_result = result_dict

    expected = [score["expected_root_cause"] for score in case_scores]
    predicted = [score["predicted_root_cause"] for score in case_scores]
    classification = _classification_metrics(expected, predicted)
    incorrect = [score for score in case_scores if not score["correct"]]
    reviewed_incorrect = [score for score in incorrect if score["review_required"]]
    automatically_accepted = [
        score for score in case_scores if not score["review_required"]
    ]
    accepted_correct = [score for score in automatically_accepted if score["correct"]]

    aggregate = {
        "policy_id": policy_id,
        "split": split_manifest["split"],
        "case_count": len(case_scores),
        "task_success_rate": statistics.fmean(
            score["task_success"] for score in case_scores
        ),
        "cause_accuracy": classification["accuracy"],
        "macro_f1": classification["macro_f1"],
        "per_class": classification["per_class"],
        "accuracy_bootstrap_95_ci": _bootstrap_accuracy_interval(
            expected, predicted
        ),
        "accuracy_wilson_95_ci": wilson_accuracy_interval(
            sum(
                expected_value == predicted_value
                for expected_value, predicted_value in zip(expected, predicted)
            ),
            len(expected),
        ),
        "citation_correctness": statistics.fmean(
            score["citation_correctness"] for score in case_scores
        ),
        "groundedness": statistics.fmean(
            score["groundedness"] for score in case_scores
        ),
        "unsupported_citation_rate": statistics.fmean(
            score["unsupported_citation_rate"] for score in case_scores
        ),
        "hallucination_rate": statistics.fmean(
            score["hallucination_rate"] for score in case_scores
        ),
        "report_quality": statistics.fmean(
            score["report_quality"] for score in case_scores
        ),
        "mean_evidence_source_diversity": statistics.fmean(
            score["evidence_source_diversity"] for score in case_scores
        ),
        "review_rate": statistics.fmean(
            float(score["review_required"]) for score in case_scores
        ),
        "review_recall": (
            len(reviewed_incorrect) / len(incorrect) if incorrect else 1.0
        ),
        "review_recall_denominator": len(incorrect),
        "automatic_coverage": len(automatically_accepted) / len(case_scores),
        "accepted_accuracy": (
            len(accepted_correct) / len(automatically_accepted)
            if automatically_accepted
            else None
        ),
        "latency_ms": {
            "p50": percentile(
                [score["latency_ms"] for score in case_scores], 0.50
            ),
            "p95": percentile(
                [score["latency_ms"] for score in case_scores], 0.95
            ),
            "p99": percentile(
                [score["latency_ms"] for score in case_scores], 0.99
            ),
            "mean": statistics.fmean(
                score["latency_ms"] for score in case_scores
            ),
        },
        "external_llm_calls": sum(
            score["external_llm_calls"] for score in case_scores
        ),
        "external_cost_usd": sum(
            score["external_cost_usd"] for score in case_scores
        ),
    }
    aggregate["selection_score"] = (
        0.40 * aggregate["task_success_rate"]
        + 0.25 * aggregate["cause_accuracy"]
        + 0.20 * aggregate["citation_correctness"]
        + 0.15 * aggregate["groundedness"]
    )
    safety_gates = {
        "task_success_at_least_0_98": aggregate["task_success_rate"] >= 0.98,
        "report_quality_at_least_0_95": aggregate["report_quality"] >= 0.95,
        "hallucination_at_most_0_05": aggregate["hallucination_rate"] <= 0.05,
        "unsupported_citations_at_most_0_02": aggregate[
            "unsupported_citation_rate"
        ]
        <= 0.02,
        "review_recall_at_least_0_95": aggregate["review_recall"] >= 0.95,
    }
    aggregate["safety_gates"] = safety_gates
    aggregate["passes_safety_gates"] = all(safety_gates.values())
    return {
        "aggregate": aggregate,
        "cases": case_scores,
        "sample_result": sample_result,
    }


def select_candidate(candidate_results: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    eligible = [
        candidate
        for candidate in candidate_results
        if candidate["aggregate"]["passes_safety_gates"]
    ]
    if not eligible:
        raise RuntimeError("No candidate passed every predeclared safety gate")
    ranked = sorted(
        eligible,
        key=lambda candidate: (
            -candidate["aggregate"]["selection_score"],
            -candidate["aggregate"]["cause_accuracy"],
            -candidate["aggregate"]["mean_evidence_source_diversity"],
            candidate["aggregate"]["latency_ms"]["p95"],
            candidate["aggregate"]["policy_id"],
        ),
    )
    return ranked[0]


def evaluate_failure_recovery(valid_payload: bytes) -> Dict[str, Any]:
    corrupt_inputs = {
        "empty": b"",
        "truncated": valid_payload[:-7],
        "wrong_stdf_version": valid_payload[:5] + bytes((3,)) + valid_payload[6:],
        "trailing_partial_header": valid_payload + b"\x01\x02",
    }
    rejected: dict[str, str] = {}
    workflow = RCAEvidenceWorkflow(
        [
            {
                "document_id": "RECOVERY_DOC",
                "root_cause": "edge_process_stress",
                "title": "Recovery fixture",
                "text": "peripheral edge failures",
            }
        ],
        "fusion_balanced_v1",
    )
    for name, payload in corrupt_inputs.items():
        try:
            workflow.analyze(payload, session_id=f"recovery-{name}")
        except ValueError as exc:
            rejected[name] = str(exc)
    return {
        "challenge_count": len(corrupt_inputs),
        "rejected_count": len(rejected),
        "rejection_rate": len(rejected) / len(corrupt_inputs),
        "details": rejected,
    }


def environment_snapshot() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or "not_reported",
        "logical_cpu_count": os.cpu_count(),
        "generator_version": GENERATOR_VERSION,
    }
