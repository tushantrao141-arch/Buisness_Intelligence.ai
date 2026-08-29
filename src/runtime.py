"""One-call application runtime used by Streamlit and tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import pandas as pd

from src.analytics import AnalysisResult, run_analytics
from src.data import DataBundle, load_data
from src.evaluation import compare_baselines, evaluate_scenarios
from src.storage import record_runtime


@dataclass(frozen=True)
class DemoRuntime:
    """Application-ready data, analysis, evaluation, and runtime measurements."""

    data: DataBundle
    analysis: AnalysisResult
    evaluation: pd.DataFrame
    benchmark: pd.DataFrame
    benchmark_detail: pd.DataFrame
    latency_ms: float


def build_demo(project_root: str | Path, force_regenerate: bool = False, persist_telemetry: bool = True) -> DemoRuntime:
    """Build the complete demo state and optionally record its runtime telemetry."""

    root = Path(project_root)
    started = perf_counter()
    data = load_data(root, force_regenerate=force_regenerate)
    analysis = run_analytics(data)
    evaluation = evaluate_scenarios(root, analysis)
    benchmark, benchmark_detail = compare_baselines(root, data, analysis)
    latency_ms = round((perf_counter() - started) * 1000, 2)
    benchmark.loc[benchmark["method"].eq("Full SilentSignal"), "evaluation_latency_ms"] = latency_ms
    if persist_telemetry:
        record_runtime(root, latency_ms)
    return DemoRuntime(data, analysis, evaluation, benchmark, benchmark_detail, latency_ms)
