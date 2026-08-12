"""Metric, safety-gate, and candidate-selection tests."""

from __future__ import annotations

from rca_evidence.evaluation import (
    evaluate_policy,
    select_candidate,
    wilson_accuracy_interval,
)
from rca_evidence.synthetic import build_knowledge_corpus, generate_dataset, load_split_manifest
from rca_evidence.workflow import POLICIES


def test_development_evaluator_scores_every_candidate(tmp_path) -> None:
    generate_dataset(tmp_path)
    development = load_split_manifest(tmp_path, "development")
    small_split = {
        **development,
        "cases": [
            development["cases"][index]
            for index in (0, 6, 12, 18, 24)
        ],
        "case_count": 5,
    }
    candidates = [
        evaluate_policy(
            tmp_path,
            small_split,
            build_knowledge_corpus(),
            policy_id,
        )
        for policy_id in POLICIES
    ]
    selected = select_candidate(candidates)

    assert len(candidates) == 4
    assert selected["aggregate"]["passes_safety_gates"]
    assert all(candidate["aggregate"]["case_count"] == 5 for candidate in candidates)
    assert all(candidate["aggregate"]["external_cost_usd"] == 0.0 for candidate in candidates)


def test_fusion_policy_uses_more_evidence_sources_than_single_path_candidates(tmp_path) -> None:
    generate_dataset(tmp_path)
    development = load_split_manifest(tmp_path, "development")
    one_case = {**development, "cases": development["cases"][:1], "case_count": 1}
    corpus = build_knowledge_corpus()
    rules = evaluate_policy(tmp_path, one_case, corpus, "rules_v1")
    retrieval = evaluate_policy(tmp_path, one_case, corpus, "retrieval_v1")
    fusion = evaluate_policy(tmp_path, one_case, corpus, "fusion_balanced_v1")

    assert rules["aggregate"]["mean_evidence_source_diversity"] == 3
    assert retrieval["aggregate"]["mean_evidence_source_diversity"] == 1
    assert fusion["aggregate"]["mean_evidence_source_diversity"] == 4


def test_wilson_interval_discloses_finite_sample_uncertainty() -> None:
    interval = wilson_accuracy_interval(25, 25)
    assert 0.86 < interval["lower_95"] < 0.87
    assert interval["upper_95"] == 1.0
