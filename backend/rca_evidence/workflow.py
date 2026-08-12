"""Six-node deterministic LangGraph RCA workflow bound to evidence policies."""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence, TypedDict

from langgraph.graph import END, START, StateGraph

from .analysis import (
    ROOT_CAUSES,
    build_retrieval_query,
    correlation_analysis,
    data_summary,
    rule_scores,
    spatial_analysis,
    statistical_analysis,
)
from .models import ParsedSTDF, StageTrace, WorkflowResult
from .persistence import SQLiteSessionStore
from .retrieval import BM25Index, RetrievalHit
from .stdf import parse_stdf_bytes


@dataclass(frozen=True)
class PolicyConfig:
    policy_id: str
    rule_weight: float
    retrieval_weight: float
    review_threshold: float
    require_three_source_types: bool


POLICIES: Dict[str, PolicyConfig] = {
    "rules_v1": PolicyConfig("rules_v1", 1.0, 0.0, 0.76, False),
    "retrieval_v1": PolicyConfig("retrieval_v1", 0.0, 1.0, 0.76, False),
    "fusion_balanced_v1": PolicyConfig(
        "fusion_balanced_v1", 0.70, 0.30, 0.78, True
    ),
    "fusion_retrieval_heavy_v1": PolicyConfig(
        "fusion_retrieval_heavy_v1", 0.45, 0.55, 0.78, True
    ),
}

_STATISTICAL_SUPPORT = {
    "CONTACT_RES": {"positive": ("probe_card_contamination",)},
    "FMAX": {
        "negative": (
            "probe_card_contamination",
            "tester_temperature_drift",
            "edge_process_stress",
        )
    },
    "FOCUS_MON": {"positive": ("lithography_focus_shift",)},
    "IDDQ": {
        "positive": (
            "edge_process_stress",
            "tester_temperature_drift",
            "random_esd_damage",
        )
    },
    "LEAKAGE": {"positive": ("random_esd_damage",)},
    "TEMP_SENSOR": {"positive": ("tester_temperature_drift",)},
    "VTH": {
        "negative": ("edge_process_stress",),
        "positive": ("lithography_focus_shift",),
    },
}

_SPATIAL_SUPPORT = {
    "peripheral_edge": ("edge_process_stress",),
    "row_or_column_stripe": ("probe_card_contamination",),
    "compact_cluster": ("lithography_focus_shift",),
    "distributed_random": (
        "tester_temperature_drift",
        "random_esd_damage",
    ),
    "no_failures": (),
}

_NEXT_STEPS = {
    "edge_process_stress": [
        "Review edge-process controls and wafer-edge metrology.",
        "Cross-section representative peripheral die before disposition.",
    ],
    "probe_card_contamination": [
        "Clean and re-qualify the probe card using an independent contact check.",
        "Repeat a bounded sample before releasing the lot.",
    ],
    "tester_temperature_drift": [
        "Verify tester thermal control and chamber calibration.",
        "Repeat temperature-sensitive tests on a controlled reference wafer.",
    ],
    "lithography_focus_shift": [
        "Review focus maps and reticle-position history.",
        "Correlate the cluster with inline lithography metrology.",
    ],
    "random_esd_damage": [
        "Inspect handling and grounding controls.",
        "Perform electrical failure analysis on a representative sample.",
    ],
}

_AGENT_NODE_NAMES = (
    "data_analyst",
    "statistical_analyst",
    "spatial_pattern_detector",
    "correlation_hunter",
    "conclusion_engine",
    "report_generator",
)


class RCAState(TypedDict, total=False):
    payload: bytes
    parsed: ParsedSTDF
    data: Dict[str, Any]
    statistical: Dict[str, Any]
    spatial: Dict[str, Any]
    correlations: Dict[str, Any]
    prediction: Dict[str, Any]
    report: Dict[str, Any]
    review_required: bool
    evidence_registry: Dict[str, Dict[str, Any]]
    traces: list[StageTrace]


def _normalize(scores: Mapping[str, float]) -> Dict[str, float]:
    maximum = max(scores.values(), default=0.0)
    if maximum <= 1e-12:
        return {root_cause: 0.0 for root_cause in ROOT_CAUSES}
    return {
        root_cause: float(scores.get(root_cause, 0.0)) / maximum
        for root_cause in ROOT_CAUSES
    }


def _retrieval_scores(hits: Sequence[RetrievalHit]) -> Dict[str, float]:
    aggregate = {root_cause: 0.0 for root_cause in ROOT_CAUSES}
    for hit in hits:
        aggregate[hit.root_cause] += hit.score
    return _normalize(aggregate)


def _supports_for_effect(test_name: str, effect: float) -> tuple[str, ...]:
    direction = "positive" if effect >= 0 else "negative"
    return tuple(_STATISTICAL_SUPPORT.get(test_name, {}).get(direction, ()))


def _confidence(ranked_scores: Sequence[tuple[str, float]]) -> float:
    if not ranked_scores:
        return 0.0
    top_score = ranked_scores[0][1]
    second_score = ranked_scores[1][1] if len(ranked_scores) > 1 else 0.0
    if top_score <= 1e-12:
        return 0.0
    margin = max(0.0, (top_score - second_score) / top_score)
    return min(0.99, 0.55 + 0.44 * math.sqrt(margin))


def _append_trace(
    state: RCAState,
    index: int,
    agent: str,
    started_at: float,
    output: Mapping[str, Any],
) -> list[StageTrace]:
    return [
        *state.get("traces", []),
        StageTrace(
            index,
            agent,
            (time.perf_counter() - started_at) * 1000,
            output,
        ),
    ]


class RCAEvidenceWorkflow:
    """Execute six deterministic agent nodes through a compiled LangGraph."""

    def __init__(
        self,
        corpus: Sequence[Mapping[str, Any]],
        policy_id: str,
        *,
        store: SQLiteSessionStore | None = None,
    ) -> None:
        if policy_id not in POLICIES:
            raise ValueError(f"Unknown policy: {policy_id}")
        self.policy = POLICIES[policy_id]
        self.retrieval_index = BM25Index(corpus)
        self.store = store
        self.graph = self._build_graph()

    @property
    def agent_node_names(self) -> tuple[str, ...]:
        return _AGENT_NODE_NAMES

    def _build_graph(self):
        graph = StateGraph(RCAState)
        graph.add_node("data_analyst", self._data_analyst_node)
        graph.add_node("statistical_analyst", self._statistical_analyst_node)
        graph.add_node(
            "spatial_pattern_detector", self._spatial_pattern_detector_node
        )
        graph.add_node("correlation_hunter", self._correlation_hunter_node)
        graph.add_node("conclusion_engine", self._conclusion_engine_node)
        graph.add_node("report_generator", self._report_generator_node)
        graph.add_edge(START, "data_analyst")
        graph.add_edge("data_analyst", "statistical_analyst")
        graph.add_edge("statistical_analyst", "spatial_pattern_detector")
        graph.add_edge("spatial_pattern_detector", "correlation_hunter")
        graph.add_edge("correlation_hunter", "conclusion_engine")
        graph.add_edge("conclusion_engine", "report_generator")
        graph.add_edge("report_generator", END)
        return graph.compile()

    def _data_analyst_node(self, state: RCAState) -> RCAState:
        started_at = time.perf_counter()
        parsed = parse_stdf_bytes(state["payload"])
        data = data_summary(parsed)
        registry = dict(state.get("evidence_registry", {}))
        registry[f"input:{parsed.file_sha256}#summary"] = {
            "source_type": "input",
            "detail": (
                f"{parsed.die_count} die, {parsed.failed_die_count} failures, "
                f"yield {parsed.yield_rate:.4f}"
            ),
            "supports": [],
        }
        return {
            "parsed": parsed,
            "data": data,
            "evidence_registry": registry,
            "traces": _append_trace(
                state, 1, "DataAnalyst", started_at, data
            ),
        }

    def _statistical_analyst_node(self, state: RCAState) -> RCAState:
        started_at = time.perf_counter()
        statistical = statistical_analysis(state["parsed"])
        registry = dict(state["evidence_registry"])
        for test_name in statistical["ranked_tests"]:
            effect = float(statistical["tests"][test_name]["effect_size"])
            registry[f"analysis:statistical#{test_name}"] = {
                "source_type": "statistical",
                "detail": f"{test_name} failed/pass effect size {effect:.4f}",
                "supports": list(_supports_for_effect(test_name, effect)),
            }
        return {
            "statistical": statistical,
            "evidence_registry": registry,
            "traces": _append_trace(
                state, 2, "StatisticalAnalyst", started_at, statistical
            ),
        }

    def _spatial_pattern_detector_node(self, state: RCAState) -> RCAState:
        started_at = time.perf_counter()
        spatial = spatial_analysis(state["parsed"])
        citation_id = f"analysis:spatial#{spatial['pattern']}"
        registry = dict(state["evidence_registry"])
        registry[citation_id] = {
            "source_type": "spatial",
            "detail": (
                f"pattern={spatial['pattern']}, edge={spatial['edge_fraction']:.4f}, "
                f"stripe={spatial['stripe_fraction']:.4f}, "
                f"component={spatial['largest_component_fraction']:.4f}"
            ),
            "supports": list(_SPATIAL_SUPPORT[str(spatial["pattern"])]),
        }
        return {
            "spatial": spatial,
            "evidence_registry": registry,
            "traces": _append_trace(
                state, 3, "SpatialPatternDetector", started_at, spatial
            ),
        }

    def _correlation_hunter_node(self, state: RCAState) -> RCAState:
        started_at = time.perf_counter()
        correlations = correlation_analysis(state["parsed"])
        registry = dict(state["evidence_registry"])
        for test_name in correlations["ranked_tests"][:4]:
            value = float(correlations["correlations"][test_name])
            registry[f"analysis:correlation#{test_name}"] = {
                "source_type": "correlation",
                "detail": f"{test_name} failure correlation {value:.4f}",
                "supports": list(_supports_for_effect(test_name, value)),
            }
        return {
            "correlations": correlations,
            "evidence_registry": registry,
            "traces": _append_trace(
                state, 4, "CorrelationHunter", started_at, correlations
            ),
        }

    def _conclusion_engine_node(self, state: RCAState) -> RCAState:
        started_at = time.perf_counter()
        data = state["data"]
        statistical = state["statistical"]
        spatial = state["spatial"]
        correlations = state["correlations"]
        registry = dict(state["evidence_registry"])

        query = build_retrieval_query(statistical, spatial)
        retrieval_hits = self.retrieval_index.search(query, limit=5)
        for hit in retrieval_hits:
            registry[f"kb:{hit.document_id}"] = {
                "source_type": "knowledge_base",
                "detail": hit.text,
                "supports": [hit.root_cause],
                "score": hit.score,
            }
        normalized_rules = _normalize(
            rule_scores(data, statistical, spatial, correlations)
        )
        normalized_retrieval = _retrieval_scores(retrieval_hits)
        combined_scores = {
            root_cause: (
                self.policy.rule_weight * normalized_rules[root_cause]
                + self.policy.retrieval_weight
                * normalized_retrieval[root_cause]
            )
            for root_cause in ROOT_CAUSES
        }
        ranked_scores = sorted(
            combined_scores.items(), key=lambda item: (-item[1], item[0])
        )
        predicted_root_cause = ranked_scores[0][0]
        rule_prediction = max(normalized_rules, key=normalized_rules.get)
        retrieval_prediction = max(
            normalized_retrieval, key=normalized_retrieval.get
        )
        confidence = _confidence(ranked_scores)

        allowed_source_types: set[str] = set()
        if self.policy.rule_weight > 0:
            allowed_source_types.update(
                {"statistical", "spatial", "correlation"}
            )
        if self.policy.retrieval_weight > 0:
            allowed_source_types.add("knowledge_base")
        supporting_citations = [
            citation_id
            for citation_id, evidence in registry.items()
            if predicted_root_cause in evidence.get("supports", [])
            and evidence.get("source_type") in allowed_source_types
        ]
        supporting_citations.sort(
            key=lambda citation_id: (
                registry[citation_id]["source_type"],
                citation_id,
            )
        )
        source_types = {
            registry[citation_id]["source_type"]
            for citation_id in supporting_citations
        }
        disagreement = rule_prediction != retrieval_prediction
        review_required = (
            confidence < self.policy.review_threshold
            or disagreement
            or (
                self.policy.require_three_source_types
                and len(source_types) < 3
            )
        )
        prediction = {
            "root_cause": predicted_root_cause,
            "confidence": confidence,
            "ranked_scores": [
                {"root_cause": root_cause, "score": score}
                for root_cause, score in ranked_scores
            ],
            "rule_prediction": rule_prediction,
            "retrieval_prediction": retrieval_prediction,
            "rule_retrieval_disagreement": disagreement,
            "citations": supporting_citations,
            "evidence_source_types": sorted(source_types),
            "retrieval_query": query,
            "retrieval_hits": [hit.to_dict() for hit in retrieval_hits],
        }
        return {
            "prediction": prediction,
            "review_required": review_required,
            "evidence_registry": registry,
            "traces": _append_trace(
                state, 5, "ConclusionEngine", started_at, prediction
            ),
        }

    def _report_generator_node(self, state: RCAState) -> RCAState:
        started_at = time.perf_counter()
        data = state["data"]
        statistical = state["statistical"]
        spatial = state["spatial"]
        correlations = state["correlations"]
        prediction = state["prediction"]
        predicted_root_cause = prediction["root_cause"]
        supporting_citations = prediction["citations"]
        spatial_citation = f"analysis:spatial#{spatial['pattern']}"
        report = {
            "title": "Synthetic STDF Root Cause Analysis",
            "executive_summary": (
                f"The evidence policy ranked {predicted_root_cause.replace('_', ' ')} "
                f"first at confidence {prediction['confidence']:.3f}."
            ),
            "input": data,
            "findings": {
                "top_statistical_tests": statistical["ranked_tests"][:4],
                "spatial_pattern": spatial["pattern"],
                "top_correlations": correlations["ranked_tests"][:4],
            },
            "ranked_hypotheses": prediction["ranked_scores"][:3],
            "citations": supporting_citations,
            "review_required": state["review_required"],
            "limitations": [
                "Evidence is generated from an independent synthetic benchmark.",
                "The policy has no authority to disposition material or control test equipment.",
                "A qualified engineer must review flagged or real-domain cases.",
            ],
            "next_steps": _NEXT_STEPS[predicted_root_cause],
            "material_claims": [
                {
                    "claim": f"Primary root cause: {predicted_root_cause}",
                    "citations": supporting_citations,
                },
                {
                    "claim": f"Spatial pattern: {spatial['pattern']}",
                    "citations": [spatial_citation],
                },
            ],
        }
        trace_output = {
            "section_count": 9,
            "material_claim_count": len(report["material_claims"]),
            "citation_count": len(supporting_citations),
        }
        return {
            "report": report,
            "traces": _append_trace(
                state, 6, "ReportGenerator", started_at, trace_output
            ),
        }

    def analyze(
        self,
        payload: bytes,
        *,
        session_id: str | None = None,
    ) -> WorkflowResult:
        workflow_start = time.perf_counter()
        active_session_id = session_id or str(uuid.uuid4())
        final_state: RCAState = self.graph.invoke(
            {
                "payload": payload,
                "evidence_registry": {},
                "traces": [],
            }
        )
        result = WorkflowResult(
            session_id=active_session_id,
            policy_id=self.policy.policy_id,
            status="completed",
            input_summary=final_state["data"],
            prediction=final_state["prediction"],
            evidence_registry=final_state["evidence_registry"],
            stage_traces=final_state["traces"],
            report=final_state["report"],
            latency_ms=(time.perf_counter() - workflow_start) * 1000,
            review_required=final_state["review_required"],
            metadata={
                "agent_count": len(_AGENT_NODE_NAMES),
                "knowledge_document_count": self.retrieval_index.document_count,
                "deterministic_local_policy": True,
                "orchestrator": "langgraph",
                "langgraph_node_count": len(_AGENT_NODE_NAMES),
            },
        )
        if self.store is not None:
            self.store.save(result)
        return result
