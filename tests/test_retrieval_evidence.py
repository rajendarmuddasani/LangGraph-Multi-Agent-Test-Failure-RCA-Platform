"""Tests for the real local BM25 retrieval boundary."""

from __future__ import annotations

from rca_evidence.retrieval import BM25Index
from rca_evidence.synthetic import build_knowledge_corpus


def test_bm25_retrieves_probe_case_from_evidence_terms() -> None:
    index = BM25Index(build_knowledge_corpus())
    hits = index.search(
        "narrow column stripe elevated contact resistance reduced fmax",
        limit=3,
    )

    assert index.document_count == 30
    assert len(hits) == 3
    assert all(hit.root_cause == "probe_card_contamination" for hit in hits)
    assert hits[0].score > 0


def test_bm25_returns_no_results_for_empty_query() -> None:
    index = BM25Index(build_knowledge_corpus())
    assert index.search("   ") == []
