"""Shared immutable data contracts for the deterministic RCA runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class DieResult:
    """One tested die reconstructed from PTR and PRR records."""

    x_coord: int
    y_coord: int
    hard_bin: int
    soft_bin: int
    passed: bool
    measurements: Mapping[str, float]
    part_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x_coord": self.x_coord,
            "y_coord": self.y_coord,
            "hard_bin": self.hard_bin,
            "soft_bin": self.soft_bin,
            "passed": self.passed,
            "measurements": dict(self.measurements),
            "part_id": self.part_id,
        }


@dataclass(frozen=True)
class ParsedSTDF:
    """Validated STDF content used by every downstream stage."""

    lot_id: str
    wafer_id: str
    dies: tuple[DieResult, ...]
    file_sha256: str
    record_counts: Mapping[str, int]
    byte_count: int

    @property
    def die_count(self) -> int:
        return len(self.dies)

    @property
    def failed_die_count(self) -> int:
        return sum(not die.passed for die in self.dies)

    @property
    def yield_rate(self) -> float:
        if not self.dies:
            return 0.0
        return sum(die.passed for die in self.dies) / len(self.dies)

    def to_summary(self) -> Dict[str, Any]:
        return {
            "lot_id": self.lot_id,
            "wafer_id": self.wafer_id,
            "die_count": self.die_count,
            "failed_die_count": self.failed_die_count,
            "yield_rate": self.yield_rate,
            "file_sha256": self.file_sha256,
            "record_counts": dict(self.record_counts),
            "byte_count": self.byte_count,
        }


@dataclass(frozen=True)
class StageTrace:
    """One measurable agent-stage execution."""

    index: int
    agent: str
    latency_ms: float
    output: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowResult:
    """Complete persisted RCA output returned by the API and benchmark."""

    session_id: str
    policy_id: str
    status: str
    input_summary: Dict[str, Any]
    prediction: Dict[str, Any]
    evidence_registry: Dict[str, Dict[str, Any]]
    stage_traces: List[StageTrace]
    report: Dict[str, Any]
    latency_ms: float
    external_llm_calls: int = 0
    external_cost_usd: float = 0.0
    review_required: bool = True
    error: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "policy_id": self.policy_id,
            "status": self.status,
            "input_summary": self.input_summary,
            "prediction": self.prediction,
            "evidence_registry": self.evidence_registry,
            "stage_traces": [trace.to_dict() for trace in self.stage_traces],
            "report": self.report,
            "latency_ms": self.latency_ms,
            "external_llm_calls": self.external_llm_calls,
            "external_cost_usd": self.external_cost_usd,
            "review_required": self.review_required,
            "error": self.error,
            "metadata": self.metadata,
        }
