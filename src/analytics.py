"""Compatibility facade re-exporting modular analytical engines."""

from __future__ import annotations

from src.graph_engine import RelationshipResult, build_relationships
from src.movement import build_kpi_history, detect_movements
from src.driver_analysis import calculate_drivers
from src.confidence import build_findings
from src.pipeline import AnalysisResult, run_pipeline as run_analytics

__all__ = [
    "RelationshipResult",
    "AnalysisResult",
    "build_relationships",
    "build_kpi_history",
    "detect_movements",
    "calculate_drivers",
    "build_findings",
    "run_analytics",
]
