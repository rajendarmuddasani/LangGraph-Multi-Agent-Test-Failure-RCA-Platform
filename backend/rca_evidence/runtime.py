"""Hash-verified loading for the selected evidence runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from .persistence import SQLiteSessionStore
from .workflow import RCAEvidenceWorkflow


class RuntimeIntegrityError(RuntimeError):
    """Raised when serving artifacts differ from evaluated identities."""


class RuntimeBundle:
    """Load and bind the selected policy, corpus, and local session store."""

    def __init__(self, repository_root: Path, database_path: Path) -> None:
        self.repository_root = repository_root.resolve()
        runtime_path = self.repository_root / "evidence" / "runtime_manifest.json"
        if not runtime_path.is_file():
            raise RuntimeIntegrityError("Runtime manifest is missing")
        self.manifest: Dict[str, Any] = json.loads(
            runtime_path.read_text(encoding="utf-8")
        )

        evaluation_path = self.repository_root / "evidence" / "model_evaluation.json"
        if not evaluation_path.is_file():
            raise RuntimeIntegrityError("Model evaluation artifact is missing")
        evaluation_bytes = evaluation_path.read_bytes()
        evaluation_hash = hashlib.sha256(evaluation_bytes).hexdigest()
        if evaluation_hash != self.manifest["model_evaluation_sha256"]:
            raise RuntimeIntegrityError("Model evaluation hash does not match runtime manifest")
        self.evaluation: Dict[str, Any] = json.loads(evaluation_bytes)

        corpus_path = self.repository_root / self.manifest["corpus_relative_path"]
        if not corpus_path.is_file():
            raise RuntimeIntegrityError("Runtime knowledge corpus is missing")
        corpus_bytes = corpus_path.read_bytes()
        corpus_hash = hashlib.sha256(corpus_bytes).hexdigest()
        if corpus_hash != self.manifest["corpus_sha256"]:
            raise RuntimeIntegrityError("Knowledge corpus hash does not match runtime manifest")
        corpus = json.loads(corpus_bytes)

        selected_policy = self.manifest["selected_policy_id"]
        evaluated_policy = self.evaluation["selected_policy_id"]
        if selected_policy != evaluated_policy:
            raise RuntimeIntegrityError("Serving policy differs from evaluated policy")

        self.store = SQLiteSessionStore(database_path)
        self.workflow = RCAEvidenceWorkflow(
            corpus,
            selected_policy,
            store=self.store,
        )

    def health_summary(self) -> Dict[str, Any]:
        confirmation = self.manifest["confirmation_metrics"]
        return {
            "status": "ready",
            "runtime_id": self.manifest["runtime_id"],
            "selected_policy_id": self.manifest["selected_policy_id"],
            "orchestrator": self.manifest["orchestrator"],
            "langgraph_version": self.manifest["langgraph_version"],
            "agent_node_count": self.manifest["agent_node_count"],
            "confirmation_case_count": confirmation["case_count"],
            "synthetic_confirmation_accuracy": confirmation["cause_accuracy"],
            "external_llm_calls": self.manifest["external_llm_calls"],
            "fail_closed": self.manifest["fail_closed"],
        }
