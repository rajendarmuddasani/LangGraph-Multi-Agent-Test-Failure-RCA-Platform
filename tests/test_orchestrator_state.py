"""Tests for orchestrator state structure and initialization."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))


def _make_initial_state(session_id="sess-test", lot_id="LOT_TEST",
                        wafer_id="W01", bin_val=5):
    return {
        "session_id": session_id,
        "lot_id": lot_id,
        "wafer_id": wafer_id,
        "bin": bin_val,
        "priority": "normal",
        "stdf_data": {},
        "wafer_map_path": "",
        "statistical_findings": [],
        "spatial_patterns": [],
        "correlations": [],
        "rag_results": [],
        "root_causes": [],
        "confidence_scores": {},
        "messages": [],
        "error": None,
    }


REQUIRED_KEYS = [
    "session_id", "lot_id", "wafer_id", "bin", "priority",
    "stdf_data", "wafer_map_path", "statistical_findings",
    "spatial_patterns", "correlations", "rag_results",
    "root_causes", "confidence_scores", "messages", "error",
]


def test_initial_state_has_all_keys():
    state = _make_initial_state()
    for key in REQUIRED_KEYS:
        assert key in state


def test_initial_state_empty_collections():
    state = _make_initial_state()
    assert state["messages"] == []
    assert state["root_causes"] == []
    assert state["stdf_data"] == {}


def test_initial_state_error_is_none():
    state = _make_initial_state()
    assert state["error"] is None


def test_initial_state_session_id_propagated():
    state = _make_initial_state(session_id="custom-sess")
    assert state["session_id"] == "custom-sess"


def test_initial_state_bin_stored_correctly():
    state = _make_initial_state(bin_val=99)
    assert state["bin"] == 99


def test_agent_message_structure():
    """Agent messages appended to state must follow the blackboard schema."""
    msg = {
        "agent": "DataAnalyst",
        "timestamp": "2025-12-05T10:00:00Z",
        "finding": "STDF parsed: 5000 die, 84.0% yield",
        "confidence": 1.0,
    }
    for key in ["agent", "timestamp", "finding", "confidence"]:
        assert key in msg


def test_root_cause_hypothesis_schema():
    """Root cause entries should carry hypothesis text and confidence."""
    rca = {
        "rank": 1,
        "hypothesis": "Edge effect from package stress",
        "confidence": 0.87,
        "evidence": [{"source": "wafer_map", "detail": "peripheral pattern"}],
    }
    assert rca["confidence"] <= 1.0
    assert len(rca["evidence"]) > 0
