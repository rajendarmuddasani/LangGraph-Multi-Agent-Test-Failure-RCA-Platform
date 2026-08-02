"""Tests for Pydantic request/response schemas."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

import pytest
from pydantic import ValidationError
from schemas.rca import (
    RCASessionCreate,
    RCASessionResponse,
    RCAStatusResponse,
    HypothesisResponse,
    AgentMessageResponse,
    RAGSearchRequest,
    RAGSearchResult,
    RAGSearchResponse,
)
from datetime import datetime


# ── RCASessionCreate ──────────────────────────────────────────────────────────

def test_rca_session_create_valid():
    s = RCASessionCreate(lot_id="LOT12345", wafer_id="W01", bin=5,
                         priority="high", user_id="user@test.com")
    assert s.lot_id == "LOT12345"
    assert s.bin == 5


def test_rca_session_create_default_priority():
    s = RCASessionCreate(lot_id="L1", wafer_id="W01", bin=0, user_id="u1")
    assert s.priority == "normal"


def test_rca_session_create_invalid_priority():
    with pytest.raises(ValidationError):
        RCASessionCreate(lot_id="L1", wafer_id="W01", bin=5,
                         priority="urgent", user_id="u1")


def test_rca_session_create_empty_lot_id():
    with pytest.raises(ValidationError):
        RCASessionCreate(lot_id="", wafer_id="W01", bin=5, user_id="u1")


def test_rca_session_create_bin_zero_allowed():
    s = RCASessionCreate(lot_id="L1", wafer_id="W01", bin=0, user_id="u1")
    assert s.bin == 0


def test_rca_session_create_all_priorities():
    for p in ["low", "normal", "high", "critical"]:
        s = RCASessionCreate(lot_id="L1", wafer_id="W01", bin=1,
                             priority=p, user_id="u1")
        assert s.priority == p


# ── RCASessionResponse ────────────────────────────────────────────────────────

def test_rca_session_response():
    r = RCASessionResponse(session_id="sess-001", status="queued",
                           message="RCA submitted successfully")
    assert r.session_id == "sess-001"
    assert r.status == "queued"


# ── RCAStatusResponse ─────────────────────────────────────────────────────────

def test_rca_status_response_valid():
    r = RCAStatusResponse(
        session_id="sess-001",
        status="running",
        progress=65,
        active_agents=["ConclusionEngine"],
        completed_agents=["DataAnalyst"],
        started_at=datetime(2024, 1, 15, 10, 30),
        completed_at=None,
    )
    assert r.progress == 65
    assert r.completed_at is None


def test_rca_status_progress_bounds():
    with pytest.raises(ValidationError):
        RCAStatusResponse(
            session_id="s", status="running", progress=101,
            active_agents=[], completed_agents=[],
            started_at=None, completed_at=None,
        )
    with pytest.raises(ValidationError):
        RCAStatusResponse(
            session_id="s", status="running", progress=-1,
            active_agents=[], completed_agents=[],
            started_at=None, completed_at=None,
        )


# ── HypothesisResponse ────────────────────────────────────────────────────────

def test_hypothesis_response_valid():
    h = HypothesisResponse(rank=1, hypothesis="Edge effect pattern",
                           confidence=0.88, evidence=[{"source": "wafer_map"}])
    assert h.rank == 1
    assert h.confidence == 0.88


def test_hypothesis_confidence_bounds():
    with pytest.raises(ValidationError):
        HypothesisResponse(rank=1, hypothesis="H", confidence=1.5, evidence=[])
    with pytest.raises(ValidationError):
        HypothesisResponse(rank=1, hypothesis="H", confidence=-0.1, evidence=[])


# ── RAGSearchRequest ──────────────────────────────────────────────────────────

def test_rag_search_request_valid():
    r = RAGSearchRequest(query="Edge effect on periphery")
    assert r.top_k == 10
    assert r.similarity_threshold == 0.6


def test_rag_search_request_empty_query():
    with pytest.raises(ValidationError):
        RAGSearchRequest(query="")


def test_rag_search_request_top_k_bounds():
    with pytest.raises(ValidationError):
        RAGSearchRequest(query="test", top_k=0)
    with pytest.raises(ValidationError):
        RAGSearchRequest(query="test", top_k=101)


# ── RAGSearchResponse ─────────────────────────────────────────────────────────

def test_rag_search_response_structure():
    result = RAGSearchResult(id="r1", score=0.92,
                             text="Edge effect detected",
                             metadata={"lot_id": "LOT123"})
    response = RAGSearchResponse(query="edge effect", results=[result],
                                 total_results=1)
    assert response.total_results == 1
    assert response.results[0].score == 0.92
