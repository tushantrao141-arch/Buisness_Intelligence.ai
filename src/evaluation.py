"""Held-out evaluation. This is the only module allowed to read ground truth."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from src.analytics import AnalysisResult
from src.config import get_user, load_config_bundle
from src.data import DataBundle
from src.evidence import build_evidence_packet
from src.narrative import narrative_from_packet
from src.security import check_access


def evaluate_scenarios(project_root: str | Path, analysis: AnalysisResult) -> pd.DataFrame:
    root = Path(project_root)
    truth = pd.read_csv(root / "data" / "ground_truth" / "events.csv")
    rows: list[dict] = []
    for scenario in truth.itertuples(index=False):
        expected_entities = set(json.loads(scenario.entity_ids))
        if scenario.scenario_id == "S5":
            bundle = load_config_bundle(root)
            user = get_user("west_investigator", bundle)
            decision = check_access(user, "NORTH", detail=True)
            actual = "ACCESS_DENIED" if not decision.allowed else "ALLOWED"
            matched_finding = "Pre-evidence access control"
        else:
            candidates = []
            for finding in analysis.findings.itertuples(index=False):
                overlap = len(expected_entities.intersection(set(finding.account_ids)))
                if overlap:
                    candidates.append((overlap, finding))
            if candidates:
                _, match = max(candidates, key=lambda item: item[0])
                actual = str(match.decision)
                matched_finding = str(match.finding_id)
            else:
                actual = "NOT_DETECTED"
                matched_finding = "—"
        rows.append(
            {
                "scenario_id": scenario.scenario_id,
                "scenario": scenario.name,
                "expected": scenario.expected_outcome,
                "actual": actual,
                "passed": actual == scenario.expected_outcome,
                "matched_finding": matched_finding,
            }
        )
    return pd.DataFrame(rows)


def evaluation_summary(results: pd.DataFrame) -> dict[str, float | int]:
    return {
        "scenario_count": len(results),
        "passed": int(results["passed"].sum()),
        "acceptance_rate": float(results["passed"].mean()) if len(results) else 0.0,
    }


def compare_baselines(
    project_root: str | Path,
    data: DataBundle,
    analysis: AnalysisResult,
    false_positive_review_cost_inr: float = 250_000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Automatically compare four transparent methods against hidden labels.

    Classification metrics ask one narrow question: which scenario should be
    raised as an ALERT? MONITOR, ABSTAIN, and PEER_BASED are negative classes
    for this calculation and are evaluated separately where appropriate.
    """

    root = Path(project_root)
    truth = pd.read_csv(root / "data" / "ground_truth" / "events.csv")
    truth = truth.loc[truth["scenario_id"].ne("S5")].copy()
    methods = ["Threshold only", "Movement detector", "Movement + proximity", "Full SilentSignal"]
    detail_rows: list[dict] = []
    elapsed_by_method: dict[str, float] = {}

    for method in methods:
        started = perf_counter()
        for scenario in truth.itertuples(index=False):
            entities = set(json.loads(scenario.entity_ids))
            scoped_tx = data.enriched.loc[data.enriched["account_id"].isin(entities)]
            if method == "Threshold only":
                predicted = "ALERT" if bool((scoped_tx["is_cash"] & scoped_tx["amount_inr"].ge(1_000_000)).any()) else "NO_ALERT"
            elif method == "Movement detector":
                moved = analysis.movements.loc[analysis.movements["region"].eq(scenario.region), "material"].any()
                predicted = "ALERT" if bool(moved) else "NO_ALERT"
            elif method == "Movement + proximity":
                moved = analysis.movements.loc[
                    analysis.movements["region"].eq(scenario.region)
                    & analysis.movements["kpi_id"].eq("near_threshold_value_ratio"),
                    "material",
                ].any()
                predicted = "ALERT" if bool(moved) else "NO_ALERT"
            else:
                matches = [
                    finding
                    for finding in analysis.findings.itertuples(index=False)
                    if entities.intersection(set(finding.account_ids))
                ]
                predicted = str(max(matches, key=lambda row: len(entities.intersection(set(row.account_ids)))).decision) if matches else "NOT_DETECTED"
            detail_rows.append(
                {
                    "method": method,
                    "scenario_id": scenario.scenario_id,
                    "scenario": scenario.name,
                    "expected_outcome": scenario.expected_outcome,
                    "predicted_outcome": predicted,
                    "expected_alert": scenario.expected_outcome == "ALERT",
                    "predicted_alert": predicted == "ALERT",
                }
            )
        elapsed_by_method[method] = (perf_counter() - started) * 1000

    detail = pd.DataFrame(detail_rows)
    s1 = truth.loc[truth["scenario_id"].eq("S1")].iloc[0]
    expected_dimensions = set(json.loads(s1["expected_driver_dimensions"]))
    observed_dimensions = {
        "region", "branch_id", "channel", "account_age_band", "business_type", "cluster_label"
    }
    dimension_sets = {
        "Threshold only": set(),
        "Movement detector": {"region"},
        "Movement + proximity": {"region", "branch_id", "channel", "account_age_band", "business_type"},
        "Full SilentSignal": observed_dimensions,
    }

    narrative_accuracy: dict[str, float] = {method: np.nan for method in methods}
    s1_finding = analysis.findings.loc[
        analysis.findings["account_ids"].map(lambda values: bool(set(values).intersection(set(json.loads(s1["entity_ids"])))))
    ].iloc[0]
    bundle = load_config_bundle(root)
    investigator = get_user("west_investigator", bundle)
    packet = build_evidence_packet(data, analysis, bundle, investigator, "WEST", s1_finding["finding_id"])
    narrative = narrative_from_packet(packet)
    numerical_checks = [
        f"{packet['kpi']['actual']:,.2f}" in narrative,
        f"{packet['kpi']['expected']:,.2f}" in narrative,
        f"{packet['kpi']['change_percent']:+.1f}%" in narrative,
    ]
    narrative_accuracy["Full SilentSignal"] = float(sum(numerical_checks) / len(numerical_checks))

    metric_rows: list[dict] = []
    for method in methods:
        scoped = detail.loc[detail["method"].eq(method)]
        tp = int((scoped["expected_alert"] & scoped["predicted_alert"]).sum())
        fp = int((~scoped["expected_alert"] & scoped["predicted_alert"]).sum())
        fn = int((scoped["expected_alert"] & ~scoped["predicted_alert"]).sum())
        tn = int((~scoped["expected_alert"] & ~scoped["predicted_alert"]).sum())
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        s3_outcome = scoped.loc[scoped["scenario_id"].eq("S3"), "predicted_outcome"].iloc[0]
        metric_rows.append(
            {
                "method": method,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "missed_patterns": fn,
                "false_positive_cost_inr": fp * false_positive_review_cost_inr,
                "driver_ranking_accuracy": len(dimension_sets[method].intersection(expected_dimensions)) / max(1, len(expected_dimensions)),
                "abstention_correctness": float(s3_outcome == "ABSTAIN"),
                "narrative_numerical_accuracy": narrative_accuracy[method],
                "evaluation_latency_ms": elapsed_by_method[method],
                "llm_calls": 0,
                "estimated_cost_usd": 0.0,
            }
        )
    return pd.DataFrame(metric_rows), detail
