"""SQLite persistence for RCA sessions, reports, and complete stage traces."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .models import WorkflowResult


class SQLiteSessionStore:
    """Small local store used by the evaluated API runtime."""

    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    policy_id TEXT NOT NULL,
                    input_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL,
                    review_required INTEGER NOT NULL,
                    result_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS stage_traces (
                    session_id TEXT NOT NULL,
                    stage_index INTEGER NOT NULL,
                    agent TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    output_json TEXT NOT NULL,
                    PRIMARY KEY (session_id, stage_index),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                        ON DELETE CASCADE
                );
                """
            )

    def save(self, result: WorkflowResult) -> None:
        result_json = json.dumps(result.to_dict(), sort_keys=True)
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO sessions (
                    session_id, created_at, policy_id, input_sha256, status,
                    review_required, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.session_id,
                    created_at,
                    result.policy_id,
                    result.input_summary["file_sha256"],
                    result.status,
                    int(result.review_required),
                    result_json,
                ),
            )
            connection.execute(
                "DELETE FROM stage_traces WHERE session_id = ?",
                (result.session_id,),
            )
            connection.executemany(
                """
                INSERT INTO stage_traces (
                    session_id, stage_index, agent, latency_ms, output_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        result.session_id,
                        trace.index,
                        trace.agent,
                        trace.latency_ms,
                        json.dumps(dict(trace.output), sort_keys=True),
                    )
                    for trace in result.stage_traces
                ],
            )

    def get(self, session_id: str) -> Dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT result_json FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row["result_json"])

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        if limit < 1 or limit > 100:
            raise ValueError("Session list limit must be between 1 and 100")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT session_id, created_at, policy_id, input_sha256, status,
                       review_required
                FROM sessions
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
