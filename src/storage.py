"""Small local audit store for actions, feedback, security, and runtime events."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


SCHEMA = """
CREATE TABLE IF NOT EXISTS runtime_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    event_type TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    model_calls INTEGER NOT NULL,
    tokens INTEGER NOT NULL,
    estimated_cost_usd REAL NOT NULL,
    cache_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS action_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    action_id TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS feedback_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    rating TEXT NOT NULL,
    correctness TEXT NOT NULL DEFAULT 'UNREVIEWED',
    corrected_driver TEXT NOT NULL DEFAULT '',
    action_decision TEXT NOT NULL DEFAULT 'NOT_REVIEWED',
    user_role TEXT NOT NULL DEFAULT '',
    comment TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id TEXT NOT NULL,
    requested_region TEXT NOT NULL,
    outcome TEXT NOT NULL,
    reason TEXT NOT NULL
);
"""


def database_path(project_root: str | Path) -> Path:
    path = Path(project_root) / "artifacts" / "silentsignal.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect(project_root: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path(project_root))
    connection.executescript(SCHEMA)
    existing = {row[1] for row in connection.execute("PRAGMA table_info(feedback_events)")}
    migrations = {
        "correctness": "TEXT NOT NULL DEFAULT 'UNREVIEWED'",
        "corrected_driver": "TEXT NOT NULL DEFAULT ''",
        "action_decision": "TEXT NOT NULL DEFAULT 'NOT_REVIEWED'",
        "user_role": "TEXT NOT NULL DEFAULT ''",
    }
    for column, definition in migrations.items():
        if column not in existing:
            connection.execute(f"ALTER TABLE feedback_events ADD COLUMN {column} {definition}")
    connection.commit()
    return connection


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_runtime(project_root: str | Path, latency_ms: float, cache_status: str = "computed") -> None:
    connection = _connect(project_root)
    try:
        connection.execute(
            "INSERT INTO runtime_events (created_at,event_type,latency_ms,model_calls,tokens,estimated_cost_usd,cache_status) VALUES (?,?,?,?,?,?,?)",
            (_now(), "full_analysis", float(latency_ms), 0, 0, 0.0, cache_status),
        )
        connection.commit()
    finally:
        connection.close()


def record_action(project_root: str | Path, user_id: str, finding_id: str, action_id: str, status: str = "APPROVED", payload: dict[str, Any] | None = None) -> None:
    connection = _connect(project_root)
    try:
        connection.execute(
            "INSERT INTO action_events (created_at,user_id,finding_id,action_id,status,payload_json) VALUES (?,?,?,?,?,?)",
            (_now(), user_id, finding_id, action_id, status, json.dumps(payload or {})),
        )
        connection.commit()
    finally:
        connection.close()


def record_feedback(
    project_root: str | Path,
    user_id: str,
    finding_id: str,
    rating: str,
    comment: str,
    correctness: str = "UNREVIEWED",
    corrected_driver: str = "",
    action_decision: str = "NOT_REVIEWED",
    user_role: str = "",
) -> None:
    connection = _connect(project_root)
    try:
        connection.execute(
            "INSERT INTO feedback_events (created_at,user_id,finding_id,rating,correctness,corrected_driver,action_decision,user_role,comment) VALUES (?,?,?,?,?,?,?,?,?)",
            (_now(), user_id, finding_id, rating, correctness, corrected_driver, action_decision, user_role, comment),
        )
        connection.commit()
    finally:
        connection.close()


def record_security(project_root: str | Path, user_id: str, requested_region: str, outcome: str, reason: str) -> None:
    connection = _connect(project_root)
    try:
        connection.execute(
            "INSERT INTO security_events (created_at,user_id,requested_region,outcome,reason) VALUES (?,?,?,?,?)",
            (_now(), user_id, requested_region, outcome, reason),
        )
        connection.commit()
    finally:
        connection.close()


def read_events(project_root: str | Path, table: str, limit: int = 50) -> pd.DataFrame:
    allowed = {"runtime_events", "action_events", "feedback_events", "security_events"}
    if table not in allowed:
        raise ValueError(f"Unsupported event table: {table}")
    connection = _connect(project_root)
    try:
        return pd.read_sql_query(
            f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?",  # table is allowlisted above
            connection,
            params=(int(limit),),
        )
    finally:
        connection.close()
