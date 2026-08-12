#!/usr/bin/env python
"""Validate deterministic data regeneration and runtime artifact identities."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rca_evidence.synthetic import generate_dataset  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_generated_data(committed_root: Path) -> dict[str, int]:
    with tempfile.TemporaryDirectory(prefix="project8-evidence-") as temporary:
        regenerated_root = Path(temporary) / "synthetic_rca_v1"
        generate_dataset(regenerated_root)
        committed_files = sorted(
            path.relative_to(committed_root)
            for path in committed_root.rglob("*")
            if path.is_file()
        )
        regenerated_files = sorted(
            path.relative_to(regenerated_root)
            for path in regenerated_root.rglob("*")
            if path.is_file()
        )
        if committed_files != regenerated_files:
            raise RuntimeError("Generated benchmark file inventory differs")
        mismatches = [
            relative_path.as_posix()
            for relative_path in committed_files
            if _sha256(committed_root / relative_path)
            != _sha256(regenerated_root / relative_path)
        ]
        if mismatches:
            raise RuntimeError(f"Generated benchmark hash mismatches: {mismatches}")
        return {
            "file_count": len(committed_files),
            "stdf_file_count": sum(path.suffix == ".stdf" for path in committed_files),
        }


def _validate_runtime_chain() -> dict[str, str]:
    runtime_path = REPOSITORY_ROOT / "evidence" / "runtime_manifest.json"
    evaluation_path = REPOSITORY_ROOT / "evidence" / "model_evaluation.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    evaluation_hash = _sha256(evaluation_path)
    if evaluation_hash != runtime["model_evaluation_sha256"]:
        raise RuntimeError("Model evaluation hash chain is invalid")
    corpus_path = REPOSITORY_ROOT / runtime["corpus_relative_path"]
    corpus_hash = _sha256(corpus_path)
    if corpus_hash != runtime["corpus_sha256"]:
        raise RuntimeError("Corpus hash chain is invalid")
    if runtime["selected_policy_id"] != evaluation["selected_policy_id"]:
        raise RuntimeError("Runtime policy differs from confirmed policy")
    if evaluation["confirmation"]["aggregate"]["case_count"] != 25:
        raise RuntimeError("Unexpected confirmation case count")
    return {
        "runtime_manifest_sha256": _sha256(runtime_path),
        "model_evaluation_sha256": evaluation_hash,
        "corpus_sha256": corpus_hash,
    }


def _validate_assets() -> dict[str, int]:
    manifest_path = REPOSITORY_ROOT / "evidence" / "assets" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    total_bytes = 0
    for asset in manifest["assets"]:
        asset_path = (REPOSITORY_ROOT / asset["path"]).resolve()
        if not asset_path.is_relative_to(REPOSITORY_ROOT):
            raise RuntimeError("Evidence asset path escapes repository root")
        if not asset_path.is_file():
            raise RuntimeError(f"Evidence asset is missing: {asset['path']}")
        if _sha256(asset_path) != asset["sha256"]:
            raise RuntimeError(f"Evidence asset hash mismatch: {asset['path']}")
        if asset_path.stat().st_size != asset["bytes"]:
            raise RuntimeError(f"Evidence asset size mismatch: {asset['path']}")
        total_bytes += asset["bytes"]
    return {"asset_count": len(manifest["assets"]), "total_bytes": total_bytes}


def main() -> int:
    data = _validate_generated_data(
        REPOSITORY_ROOT / "data" / "synthetic_rca_v1"
    )
    runtime = _validate_runtime_chain()
    assets = _validate_assets()
    print(
        json.dumps(
            {"status": "pass", "data": data, "runtime": runtime, "assets": assets},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
