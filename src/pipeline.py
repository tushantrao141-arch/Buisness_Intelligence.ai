"""End-to-end analytical pipeline orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from src.config import load_config_bundle
from src.data import DataBundle
from src.graph_engine import RelationshipResult, build_relationships
from src.movement import build_kpi_history, detect_movements
from src.driver_analysis import calculate_drivers
from src.confidence import build_findings


@dataclass(frozen=True)
class AnalysisResult:
    """Complete deterministic output consumed by evidence, evaluation, and UI layers."""

    history: pd.DataFrame
    movements: pd.DataFrame
    drivers: pd.DataFrame
    findings: pd.DataFrame
    relationships: RelationshipResult


def run_pipeline(data: DataBundle) -> AnalysisResult:
    """Execute complete deterministic pipeline across all tested components."""
    bundle = load_config_bundle()
    settings = bundle.settings.analysis
    relationships = build_relationships(
        data,
        review_score_threshold=settings.review_score_threshold,
        minimum_near_events=settings.connected_pattern_minimum_near_events,
        minimum_active_account_coverage=settings.connected_pattern_minimum_account_coverage,
    )
    history = build_kpi_history(
        data,
        relationships,
        review_score_threshold=settings.review_score_threshold,
    )
    movements = detect_movements(history, bundle.kpis)
    drivers = calculate_drivers(data, relationships)
    findings = build_findings(data, relationships)
    return AnalysisResult(history, movements, drivers, findings, relationships)
