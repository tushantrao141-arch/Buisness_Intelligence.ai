"""Run the complete demo pipeline and print held-out acceptance results."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.runtime import build_demo  # noqa: E402


if __name__ == "__main__":
    runtime = build_demo(PROJECT_ROOT, persist_telemetry=False)
    print(runtime.evaluation.to_string(index=False))
    print("\nFour-method comparison")
    print(runtime.benchmark.to_string(index=False))
    print(f"\nRuntime: {runtime.latency_ms:,.0f} ms")
