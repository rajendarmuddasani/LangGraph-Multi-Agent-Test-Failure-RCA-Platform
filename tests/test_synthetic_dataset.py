"""Determinism, provenance, and split-isolation tests for benchmark data."""

from __future__ import annotations

import hashlib
import json

from rca_evidence.stdf import parse_stdf_bytes
from rca_evidence.synthetic import (
    ROOT_CAUSES,
    build_knowledge_corpus,
    case_definitions,
    generate_case_bytes,
    generate_dataset,
)


def test_case_generation_is_deterministic_and_parseable() -> None:
    case = case_definitions()[0]
    first = generate_case_bytes(case)
    second = generate_case_bytes(case)
    parsed = parse_stdf_bytes(first)

    assert first == second
    assert parsed.die_count == 144
    assert 0 < parsed.failed_die_count < parsed.die_count
    assert len(parsed.dies[0].measurements) == 7


def test_dataset_manifest_has_disjoint_groups_and_expected_counts(tmp_path) -> None:
    manifest = generate_dataset(tmp_path)
    cases = []
    for split in ("development", "validation", "confirmation"):
        split_path = tmp_path / manifest["split_manifests"][split]["relative_path"]
        split_payload = json.loads(split_path.read_text(encoding="utf-8"))
        cases.extend(split_payload["cases"])
    split_groups = {
        split: {case["group_id"] for case in cases if case["split"] == split}
        for split in ("development", "validation", "confirmation")
    }

    assert manifest["split_counts"] == {
        "development": 30,
        "validation": 20,
        "confirmation": 25,
    }
    assert manifest["case_count"] == 75
    assert manifest["die_count"] == 10_800
    assert manifest["measurement_count"] == 75_600
    assert "cases" not in manifest
    assert split_groups["development"].isdisjoint(split_groups["validation"])
    assert split_groups["development"].isdisjoint(split_groups["confirmation"])
    assert split_groups["validation"].isdisjoint(split_groups["confirmation"])

    for case in cases:
        payload = (tmp_path / case["relative_path"]).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == case["file_sha256"]


def test_knowledge_corpus_covers_every_root_cause_without_input_ids() -> None:
    corpus = build_knowledge_corpus()
    assert len(corpus) == 30
    assert {document["root_cause"] for document in corpus} == set(ROOT_CAUSES)
    assert all(document["provenance"] == "independently_generated_synthetic" for document in corpus)
