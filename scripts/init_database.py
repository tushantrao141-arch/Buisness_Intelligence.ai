"""Initialize, verify, and seed the SQLite audit database."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.storage import _connect, database_path, read_events, record_action, record_feedback, record_runtime, record_security


def initialize_database(project_root: str | Path = PROJECT_ROOT) -> None:
    root = Path(project_root)
    db_file = database_path(root)
    print(f"Checking database at: {db_file}")

    conn = _connect(root)
    cursor = conn.cursor()
    tables = [
        row[0]
        for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if not row[0].startswith("sqlite_")
    ]
    print(f"Verified tables: {tables}")

    # Seed demo events if empty
    if len(read_events(root, "runtime_events")) == 0:
        record_runtime(root, 2840.5, "computed")
    if len(read_events(root, "action_events")) == 0:
        record_action(
            root,
            "compliance_head",
            "SS-W-005",
            "allocate_investigation_capacity",
            "ACCEPTED",
            {"region": "WEST", "confidence": 0.82},
        )
    if len(read_events(root, "feedback_events")) == 0:
        record_feedback(
            root,
            "compliance_head",
            "SS-W-005",
            "Useful",
            "Accurate driver breakdown across branches.",
            "Correct",
            "connected_accounts",
            "Accepted",
            "compliance_head",
        )
    if len(read_events(root, "security_events")) == 0:
        record_security(
            root,
            "west_investigator",
            "NORTH",
            "ACCESS_DENIED",
            "Pre-evidence entitlement enforcement",
        )

    for table in sorted(tables):
        count = cursor.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"  • {table}: {count} rows")

    conn.close()
    print("Database verified and healthy.")


if __name__ == "__main__":
    initialize_database()
