"""Authenticated API, persistence, report, and integrity contracts."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evidence_app import MAX_UPLOAD_BYTES, create_app
from rca_evidence.runtime import RuntimeBundle, RuntimeIntegrityError


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
API_KEY = "test-evidence-api-key"


def _client(tmp_path: Path) -> TestClient:
    app = create_app(
        repository_root=REPOSITORY_ROOT,
        database_path=tmp_path / "sessions.sqlite3",
        api_key=API_KEY,
    )
    return TestClient(app)


def _sample_payload() -> bytes:
    return (
        REPOSITORY_ROOT
        / "data"
        / "synthetic_rca_v1"
        / "cases"
        / "development"
        / "DEV_001.stdf"
    ).read_bytes()


def test_health_and_manifest_expose_selected_evidence_runtime(tmp_path) -> None:
    with _client(tmp_path) as client:
        health = client.get("/health")
        manifest = client.get("/api/v1/evidence/manifest")
        user_interface = client.get("/")
        favicon = client.get("/favicon.ico")

    assert health.status_code == 200
    assert health.json()["selected_policy_id"] == "fusion_balanced_v1"
    assert health.json()["orchestrator"] == "langgraph"
    assert health.json()["langgraph_version"] == "1.2.10"
    assert health.json()["agent_node_count"] == 6
    assert health.json()["api_key_configured"] is True
    assert manifest.json()["data_scope"] == "independently_generated_synthetic"
    assert "STDF RCA Workbench" in user_interface.text
    assert favicon.status_code == 200
    assert favicon.headers["content-type"] == "image/x-icon"


def test_analysis_requires_key_then_persists_session_and_report(tmp_path) -> None:
    payload = _sample_payload()
    with _client(tmp_path) as client:
        unauthorized = client.post(
            "/api/v1/evidence/analyze",
            files={"file": ("DEV_001.stdf", payload, "application/octet-stream")},
        )
        response = client.post(
            "/api/v1/evidence/analyze",
            headers={"X-API-Key": API_KEY},
            files={"file": ("DEV_001.stdf", payload, "application/octet-stream")},
        )
        result = response.json()
        session = client.get(
            f"/api/v1/evidence/sessions/{result['session_id']}",
            headers={"X-API-Key": API_KEY},
        )
        report = client.get(
            f"/api/v1/evidence/sessions/{result['session_id']}/report",
            headers={"X-API-Key": API_KEY},
        )

    assert unauthorized.status_code == 401
    assert response.status_code == 200
    assert result["policy_id"] == "fusion_balanced_v1"
    assert len(result["stage_traces"]) == 6
    assert session.status_code == 200
    assert report.status_code == 200
    assert "Synthetic STDF Root Cause Analysis" in report.text


@pytest.mark.parametrize(
    "filename,payload,expected_status",
    [
        ("input.txt", b"not stdf", 415),
        ("input.stdf", b"broken", 422),
        ("input.stdf", b"x" * (MAX_UPLOAD_BYTES + 1), 413),
    ],
    ids=("wrong-extension", "corrupt-stdf", "oversized-stdf"),
)
def test_upload_boundary_fails_closed(
    tmp_path, filename: str, payload: bytes, expected_status: int
) -> None:
    with _client(tmp_path) as client:
        response = client.post(
            "/api/v1/evidence/analyze",
            headers={"X-API-Key": API_KEY},
            files={"file": (filename, payload, "application/octet-stream")},
        )
    assert response.status_code == expected_status


def test_runtime_rejects_tampered_corpus(tmp_path) -> None:
    (tmp_path / "evidence").mkdir()
    (tmp_path / "data" / "synthetic_rca_v1").mkdir(parents=True)
    for name in ("runtime_manifest.json", "model_evaluation.json"):
        shutil.copy2(
            REPOSITORY_ROOT / "evidence" / name,
            tmp_path / "evidence" / name,
        )
    corpus = json.loads(
        (
            REPOSITORY_ROOT
            / "data"
            / "synthetic_rca_v1"
            / "corpus.json"
        ).read_text(encoding="utf-8")
    )
    corpus[0]["text"] = "tampered"
    (tmp_path / "data" / "synthetic_rca_v1" / "corpus.json").write_text(
        json.dumps(corpus),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeIntegrityError, match="corpus hash"):
        RuntimeBundle(tmp_path, tmp_path / "runtime" / "sessions.sqlite3")
