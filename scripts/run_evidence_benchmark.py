#!/usr/bin/env python
"""Run development, validation selection, sealed confirmation, or replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rca_evidence.evaluation import (  # noqa: E402
    canonical_json_bytes,
    environment_snapshot,
    evaluate_failure_recovery,
    evaluate_policy,
    select_candidate,
    write_json,
)
from rca_evidence.synthetic import load_manifest, load_split_manifest  # noqa: E402
from rca_evidence.workflow import POLICIES  # noqa: E402


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_corpus(data_root: Path, manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    corpus_bytes = (data_root / "corpus.json").read_bytes()
    if hashlib.sha256(corpus_bytes).hexdigest() != manifest["corpus_sha256"]:
        raise RuntimeError("Knowledge corpus hash does not match dataset manifest")
    return json.loads(corpus_bytes)


def _candidate_payload(
    phase: str,
    manifest: Mapping[str, Any],
    split_manifest: Mapping[str, Any],
    corpus: list[dict[str, Any]],
    data_root: Path,
) -> dict[str, Any]:
    candidates = [
        evaluate_policy(data_root, split_manifest, corpus, policy_id)
        for policy_id in POLICIES
    ]
    return {
        "schema_version": 1,
        "phase": phase,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_manifest_sha256": hashlib.sha256(
            canonical_json_bytes(manifest)
        ).hexdigest(),
        "split_manifest_sha256": manifest["split_manifests"][phase]["sha256"],
        "selection_objective": (
            "0.40*task_success + 0.25*cause_accuracy + "
            "0.20*citation_correctness + 0.15*groundedness"
        ),
        "candidates": candidates,
        "environment": environment_snapshot(),
    }


def run_development(data_root: Path, evidence_root: Path) -> None:
    manifest = load_manifest(data_root)
    split_manifest = load_split_manifest(data_root, "development")
    corpus = _load_corpus(data_root, manifest)
    payload = _candidate_payload(
        "development", manifest, split_manifest, corpus, data_root
    )
    write_json(evidence_root / "development_results.json", payload)
    print(
        json.dumps(
            {
                candidate["aggregate"]["policy_id"]: {
                    "accuracy": candidate["aggregate"]["cause_accuracy"],
                    "score": candidate["aggregate"]["selection_score"],
                    "gates": candidate["aggregate"]["passes_safety_gates"],
                }
                for candidate in payload["candidates"]
            },
            indent=2,
        )
    )


def run_selection(data_root: Path, evidence_root: Path) -> None:
    if (evidence_root / "model_evaluation.json").exists():
        raise RuntimeError(
            "Confirmation evidence already exists; selection cannot be changed"
        )
    manifest = load_manifest(data_root)
    split_manifest = load_split_manifest(data_root, "validation")
    corpus = _load_corpus(data_root, manifest)
    payload = _candidate_payload(
        "validation", manifest, split_manifest, corpus, data_root
    )
    selected = select_candidate(payload["candidates"])
    candidate_sha256 = write_json(evidence_root / "candidate_results.json", payload)
    selection = {
        "schema_version": 1,
        "selected_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_policy_id": selected["aggregate"]["policy_id"],
        "selection_score": selected["aggregate"]["selection_score"],
        "validation_metrics": selected["aggregate"],
        "candidate_results_sha256": candidate_sha256,
        "confirmation_manifest_sha256": manifest["split_manifests"][
            "confirmation"
        ]["sha256"],
        "confirmation_opened": False,
    }
    write_json(evidence_root / "selection.json", selection)
    print(json.dumps(selection, indent=2))


def run_confirmation(data_root: Path, evidence_root: Path) -> None:
    evaluation_path = evidence_root / "model_evaluation.json"
    if evaluation_path.exists():
        raise RuntimeError(
            "Confirmation was already opened. Use --stage replay for verification."
        )
    selection_path = evidence_root / "selection.json"
    if not selection_path.exists():
        raise RuntimeError("Run validation selection before opening confirmation")
    selection = _load_json(selection_path)
    if selection["confirmation_opened"]:
        raise RuntimeError("Selection state already marks confirmation as opened")

    manifest = load_manifest(data_root)
    confirmation_path = data_root / manifest["split_manifests"]["confirmation"][
        "relative_path"
    ]
    confirmation_bytes = confirmation_path.read_bytes()
    if hashlib.sha256(confirmation_bytes).hexdigest() != selection[
        "confirmation_manifest_sha256"
    ]:
        raise RuntimeError("Confirmation manifest hash changed after selection")
    split_manifest = json.loads(confirmation_bytes)
    corpus = _load_corpus(data_root, manifest)
    selected_policy = selection["selected_policy_id"]
    confirmation = evaluate_policy(
        data_root, split_manifest, corpus, selected_policy
    )
    first_case = split_manifest["cases"][0]
    failure_recovery = evaluate_failure_recovery(
        (data_root / first_case["relative_path"]).read_bytes()
    )
    sample_result = confirmation.pop("sample_result")
    evaluation = {
        "schema_version": 1,
        "confirmed_at_utc": datetime.now(timezone.utc).isoformat(),
        "selected_policy_id": selected_policy,
        "selection": selection,
        "confirmation": confirmation,
        "failure_recovery": failure_recovery,
        "data_scope": {
            "provenance": manifest["provenance"],
            "license": manifest["license"],
            "case_count": manifest["case_count"],
            "split_counts": manifest["split_counts"],
            "knowledge_document_count": manifest["knowledge_document_count"],
            "die_count": manifest["die_count"],
            "measurement_count": manifest["measurement_count"],
        },
        "environment": environment_snapshot(),
        "limitations": [
            "Independent synthetic benchmark only; no real-domain accuracy claim.",
            "Local latency is not a production service-level objective.",
            "The deterministic policy makes zero external LLM calls.",
        ],
    }
    evaluation_sha256 = write_json(evaluation_path, evaluation)
    write_json(evidence_root / "sample_confirmation_report.json", sample_result)
    write_json(
        evidence_root / "sample_retrieval_trace.json",
        {
            "session_id": sample_result["session_id"],
            "query": sample_result["prediction"]["retrieval_query"],
            "hits": sample_result["prediction"]["retrieval_hits"],
            "citations": sample_result["prediction"]["citations"],
        },
    )
    runtime_manifest = {
        "schema_version": 1,
        "runtime_id": "synthetic-rca-evidence-v1",
        "selected_policy_id": selected_policy,
        "corpus_relative_path": "data/synthetic_rca_v1/corpus.json",
        "corpus_sha256": manifest["corpus_sha256"],
        "model_evaluation_sha256": evaluation_sha256,
        "confirmation_metrics": confirmation["aggregate"],
        "external_llm_calls": 0,
        "external_cost_usd": 0.0,
        "fail_closed": True,
    }
    write_json(evidence_root / "runtime_manifest.json", runtime_manifest)
    selection["confirmation_opened"] = True
    selection["confirmation_opened_at_utc"] = evaluation["confirmed_at_utc"]
    write_json(selection_path, selection)
    print(json.dumps(evaluation["confirmation"]["aggregate"], indent=2))


def run_replay(data_root: Path, evidence_root: Path) -> None:
    expected = _load_json(evidence_root / "model_evaluation.json")
    selection = _load_json(evidence_root / "selection.json")
    manifest = load_manifest(data_root)
    split_manifest = load_split_manifest(data_root, "confirmation")
    corpus = _load_corpus(data_root, manifest)
    actual = evaluate_policy(
        data_root,
        split_manifest,
        corpus,
        selection["selected_policy_id"],
    )
    expected_aggregate = expected["confirmation"]["aggregate"]
    actual_aggregate = actual["aggregate"]
    stable_keys = (
        "case_count",
        "task_success_rate",
        "cause_accuracy",
        "macro_f1",
        "citation_correctness",
        "groundedness",
        "unsupported_citation_rate",
        "hallucination_rate",
        "report_quality",
        "review_rate",
        "review_recall",
        "automatic_coverage",
        "accepted_accuracy",
        "external_llm_calls",
        "external_cost_usd",
    )
    mismatches = {
        key: {"expected": expected_aggregate[key], "actual": actual_aggregate[key]}
        for key in stable_keys
        if expected_aggregate[key] != actual_aggregate[key]
    }
    if mismatches:
        raise RuntimeError(f"Evidence replay mismatch: {mismatches}")
    print(json.dumps({"status": "pass", "stable_metrics": list(stable_keys)}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=("development", "select", "confirm", "replay"),
        required=True,
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=REPOSITORY_ROOT / "data" / "synthetic_rca_v1",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        default=REPOSITORY_ROOT / "evidence",
    )
    arguments = parser.parse_args()
    if arguments.stage == "development":
        run_development(arguments.data_root, arguments.evidence_root)
    elif arguments.stage == "select":
        run_selection(arguments.data_root, arguments.evidence_root)
    elif arguments.stage == "confirm":
        run_confirmation(arguments.data_root, arguments.evidence_root)
    else:
        run_replay(arguments.data_root, arguments.evidence_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
