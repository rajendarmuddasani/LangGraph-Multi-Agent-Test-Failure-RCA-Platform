"""End-to-end contracts for the six-stage evaluated workflow."""

from __future__ import annotations

from rca_evidence.persistence import SQLiteSessionStore
from rca_evidence.synthetic import build_knowledge_corpus, case_definitions, generate_case_bytes
from rca_evidence.workflow import POLICIES, RCAEvidenceWorkflow


EXPECTED_AGENTS = [
    "DataAnalyst",
    "StatisticalAnalyst",
    "SpatialPatternDetector",
    "CorrelationHunter",
    "ConclusionEngine",
    "ReportGenerator",
]


def test_six_stage_workflow_predicts_and_cites_real_input() -> None:
    case = case_definitions()[0]
    workflow = RCAEvidenceWorkflow(build_knowledge_corpus(), "fusion_balanced_v1")
    result = workflow.analyze(generate_case_bytes(case), session_id="session-test")

    assert result.status == "completed"
    assert result.prediction["root_cause"] == case.expected_root_cause
    assert workflow.agent_node_names == (
        "data_analyst",
        "statistical_analyst",
        "spatial_pattern_detector",
        "correlation_hunter",
        "conclusion_engine",
        "report_generator",
    )
    assert set(workflow.graph.get_graph().nodes).issuperset(
        workflow.agent_node_names
    )
    assert [trace.agent for trace in result.stage_traces] == EXPECTED_AGENTS
    assert result.external_llm_calls == 0
    assert result.external_cost_usd == 0.0
    assert result.prediction["citations"]
    assert len(result.prediction["evidence_source_types"]) >= 3
    for citation_id in result.prediction["citations"]:
        assert citation_id in result.evidence_registry
        assert case.expected_root_cause in result.evidence_registry[citation_id]["supports"]


def test_workflow_persists_result_and_stage_traces(tmp_path) -> None:
    case = case_definitions()[1]
    store = SQLiteSessionStore(tmp_path / "sessions.sqlite3")
    workflow = RCAEvidenceWorkflow(
        build_knowledge_corpus(),
        "fusion_balanced_v1",
        store=store,
    )
    result = workflow.analyze(generate_case_bytes(case), session_id="persisted-session")
    reloaded = store.get("persisted-session")

    assert reloaded is not None
    assert reloaded["prediction"] == result.prediction
    assert len(reloaded["stage_traces"]) == 6
    assert store.list_sessions()[0]["session_id"] == "persisted-session"


def test_all_predeclared_candidates_complete_same_case() -> None:
    case = case_definitions()[7]
    payload = generate_case_bytes(case)
    for policy_id in POLICIES:
        result = RCAEvidenceWorkflow(
            build_knowledge_corpus(), policy_id
        ).analyze(payload, session_id=policy_id)
        assert result.status == "completed"
        assert len(result.stage_traces) == 6
        assert result.report["material_claims"]
