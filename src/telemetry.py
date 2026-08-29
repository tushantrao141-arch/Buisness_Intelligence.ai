"""Optional trace helpers. The Streamlit app records audit events via `storage`."""

from __future__ import annotations

import uuid
from pathlib import Path


def generate_trace_id() -> str:
    return f"TRC-{uuid.uuid4().hex[:12].upper()}"


def record_trace_event(
    project_root: str | Path,
    trace_id: str,
    stage_name: str,
    latency_ms: float,
    status: str = "SUCCESS",
    detail: str = "",
) -> None:
    """Placeholder for per-stage timing. Audit writes go through `src.storage`."""
    return None
