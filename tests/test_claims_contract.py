"""Cross-check public wording against canonical Project 08 artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALID_CLASSES = {
    "reproduced",
    "measured",
    "historical",
    "target",
    "architecture",
    "unsupported",
}


def test_public_claims_match_canonical_evidence() -> None:
    claims = json.loads(
        (REPOSITORY_ROOT / "evidence" / "claims.json").read_text(
            encoding="utf-8"
        )
    )
    evaluation_path = REPOSITORY_ROOT / "evidence" / "model_evaluation.json"
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    runtime_path = REPOSITORY_ROOT / "evidence" / "runtime_manifest.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
    validation = json.loads(
        (REPOSITORY_ROOT / "evidence" / "local_validation.json").read_text(
            encoding="utf-8"
        )
    )
    aggregate = evaluation["confirmation"]["aggregate"]

    assert {claim["evidence_class"] for claim in claims["claims"]} <= VALID_CLASSES
    assert claims["selected_policy_id"] == runtime["selected_policy_id"]
    assert runtime["orchestrator"] == "langgraph"
    assert runtime["langgraph_version"] == "1.2.10"
    assert claims["artifact_identity"]["runtime_manifest_sha256"] == hashlib.sha256(
        runtime_path.read_bytes()
    ).hexdigest()
    assert aggregate["case_count"] == 25
    assert aggregate["cause_accuracy"] == 1.0
    assert aggregate["automatic_coverage"] == 0.72
    assert aggregate["accuracy_wilson_95_ci"]["lower_95"] == 0.8668077490609515
    assert validation["tests"]["passed"] == 23
    assert validation["tests"]["coverage_percent"] == 91
    assert validation["security"]["pip_audit"]["known_vulnerabilities"] == 0
    assert hashlib.sha256(evaluation_path.read_bytes()).hexdigest() == runtime[
        "model_evaluation_sha256"
    ]
    assert "86.68% to 100% Wilson 95% interval" in readme
    assert "72% / 100%" in readme
    assert "Synthetic data only; no real-domain accuracy claim." in readme
