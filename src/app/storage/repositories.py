from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from src.app.core.config import get_settings
from src.app.core.tracing import utc_now


class SQLiteStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.db_path = Path(settings.store_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        settings.trace_export_dir.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @staticmethod
    def now() -> str:
        return utc_now()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    request_type TEXT NOT NULL,
                    primary_intent TEXT NOT NULL,
                    secondary_intents_json TEXT NOT NULL,
                    selected_agents_json TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    repo_scope_json TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    skill_versions_json TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    result_json TEXT,
                    trace_id TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS traces (
                    run_id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    exported_at TEXT,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def upsert_run(self, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs (
                    run_id, status, created_at, completed_at, request_type, primary_intent,
                    secondary_intents_json, selected_agents_json, user_id, repo_scope_json,
                    model_version, skill_versions_json, request_json, result_json, trace_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status=excluded.status,
                    completed_at=excluded.completed_at,
                    request_type=excluded.request_type,
                    primary_intent=excluded.primary_intent,
                    secondary_intents_json=excluded.secondary_intents_json,
                    selected_agents_json=excluded.selected_agents_json,
                    user_id=excluded.user_id,
                    repo_scope_json=excluded.repo_scope_json,
                    model_version=excluded.model_version,
                    skill_versions_json=excluded.skill_versions_json,
                    request_json=excluded.request_json,
                    result_json=excluded.result_json,
                    trace_id=excluded.trace_id
                """,
                (
                    payload["run_id"],
                    payload["status"],
                    payload["created_at"],
                    payload.get("completed_at"),
                    payload["request_type"],
                    payload["primary_intent"],
                    json.dumps(payload.get("secondary_intents", []), ensure_ascii=False),
                    json.dumps(payload.get("selected_agents", []), ensure_ascii=False),
                    payload["user_id"],
                    json.dumps(payload.get("repo_scope", []), ensure_ascii=False),
                    payload["model_version"],
                    json.dumps(payload.get("skill_versions", {}), ensure_ascii=False),
                    json.dumps(payload["request"], ensure_ascii=False),
                    json.dumps(payload.get("result"), ensure_ascii=False) if payload.get("result") else None,
                    payload["trace_id"],
                ),
            )

    def save_trace(self, run_id: str, trace_id: str, payload: dict[str, Any]) -> str:
        exported_at = self.now()
        settings = get_settings()
        export_path = settings.trace_export_dir / f"{run_id}.json"
        export_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO traces (run_id, trace_id, payload_json, exported_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    trace_id=excluded.trace_id,
                    payload_json=excluded.payload_json,
                    exported_at=excluded.exported_at
                """,
                (run_id, trace_id, json.dumps(payload, ensure_ascii=False), exported_at),
            )
        return exported_at

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        return {
            "run_id": row["run_id"],
            "status": row["status"],
            "created_at": row["created_at"],
            "completed_at": row["completed_at"],
            "request_type": row["request_type"],
            "primary_intent": row["primary_intent"],
            "secondary_intents": json.loads(row["secondary_intents_json"]),
            "selected_agents": json.loads(row["selected_agents_json"]),
            "user_id": row["user_id"],
            "repo_scope": json.loads(row["repo_scope_json"]),
            "model_version": row["model_version"],
            "skill_versions": json.loads(row["skill_versions_json"]),
            "request": json.loads(row["request_json"]),
            "result": json.loads(row["result_json"]) if row["result_json"] else {},
            "trace_id": row["trace_id"],
        }

    def get_trace(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM traces WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        payload = json.loads(row["payload_json"])
        payload["exported_at"] = row["exported_at"]
        return payload

    def save_feedback(self, feedback_id: str, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO feedback (feedback_id, run_id, payload_json, created_at) VALUES (?, ?, ?, ?)",
                (feedback_id, payload["run_id"], json.dumps(payload, ensure_ascii=False), self.now()),
            )


store = SQLiteStore()
