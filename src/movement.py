"""Historical baseline calculation, materiality detection, and movement ranking."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data import DataBundle
from src.graph_engine import RelationshipResult
from src.kpi_engine import alert_investigation_yield, case_sla_risk, high_risk_cluster_count, linked_pattern_exposure, near_threshold_value_ratio


def _kpi_row(date: pd.Timestamp, region: str, kpi_id: str, value: float) -> dict:
    return {"date": date, "region": region, "kpi_id": kpi_id, "value": float(value)}


def build_kpi_history(data: DataBundle, relationships: RelationshipResult) -> pd.DataFrame:
    """Build same-grain historical timeline for all 5 KPIs across all regions."""
    tx = data.enriched.merge(
        relationships.transaction_clusters[["transaction_id", "cluster_id", "qualifies"]],
        on="transaction_id",
        how="left",
    )
    tx["qualifies"] = tx["qualifies"].eq(True)
    dates = pd.date_range(tx["date"].min(), data.as_of.floor("D"), freq="D", tz="UTC")
    rows: list[dict] = []

    for date in dates:
        for region in ["ALL", "NORTH", "SOUTH", "EAST", "WEST"]:
            daily = tx.loc[tx["date"].eq(date)]
            if region != "ALL":
                daily = daily.loc[daily["region"].eq(region)]
            near_ratio = near_threshold_value_ratio(daily)
            qualifying_ids = set(daily.loc[daily["qualifies"], "transaction_id"].astype(str))
            linked = linked_pattern_exposure(daily, qualifying_ids)
            cluster_inputs = daily.loc[daily["qualifies"], ["cluster_id"]].dropna().assign(review_score=60)
            cluster_count = float(high_risk_cluster_count(cluster_inputs))

            cases = data.cases
            if region != "ALL":
                cases = cases.loc[cases["region"].eq(region)]
            closed = cases.loc[
                cases["status"].str.startswith("CLOSED")
                & cases["opened_at"].between(date - pd.Timedelta(days=28), date + pd.Timedelta(days=1), inclusive="left")
            ]
            yield_value = alert_investigation_yield(closed)
            eligible_cases = cases.loc[cases["opened_at"].le(date + pd.Timedelta(days=1))]
            active_count = case_sla_risk(eligible_cases, date, 24)
            rows.extend(
                [
                    _kpi_row(date, region, "near_threshold_value_ratio", near_ratio),
                    _kpi_row(date, region, "linked_pattern_exposure", linked),
                    _kpi_row(date, region, "high_risk_cluster_count", cluster_count),
                    _kpi_row(date, region, "alert_investigation_yield", yield_value),
                    _kpi_row(date, region, "case_sla_risk", float(active_count)),
                ]
            )
    return pd.DataFrame(rows)


def detect_movements(history: pd.DataFrame) -> pd.DataFrame:
    """Detect material movements against 28-day historical baselines."""
    rows: list[dict] = []
    for (region, kpi_id), group in history.groupby(["region", "kpi_id"]):
        ordered = group.sort_values("date")
        latest_date = ordered["date"].max()
        current = ordered.loc[ordered["date"].gt(latest_date - pd.Timedelta(days=7)), "value"]
        baseline = ordered.loc[
            ordered["date"].between(latest_date - pd.Timedelta(days=35), latest_date - pd.Timedelta(days=7), inclusive="left"),
            "value",
        ]
        if kpi_id in {"linked_pattern_exposure"}:
            actual = float(current.sum())
            expected = float(baseline.sum() / max(1, len(baseline)) * len(current))
        elif kpi_id in {"high_risk_cluster_count", "case_sla_risk"}:
            actual = float(current.iloc[-1])
            expected = float(baseline.mean()) if len(baseline) else 0.0
        else:
            actual = float(current.mean())
            expected = float(baseline.mean()) if len(baseline) else 0.0

        std = float(baseline.std(ddof=0)) if len(baseline) else 0.0
        z_score = (actual - expected) / std if std > 1e-9 else (4.0 if actual > expected and actual > 0 else 0.0)
        delta = actual - expected
        delta_pct = delta / abs(expected) * 100 if abs(expected) > 1e-9 else (100.0 if actual > 0 else 0.0)

        if kpi_id in {"near_threshold_value_ratio", "alert_investigation_yield"}:
            material = abs(delta) >= 5 and abs(z_score) >= 1.5
        elif kpi_id == "linked_pattern_exposure":
            material = delta > 5_000_000 and z_score >= 1.5
        else:
            material = delta >= 2 or z_score >= 2

        impact = min(100.0, abs(z_score) * 18 + min(abs(delta_pct), 200) * 0.22)
        rows.append(
            {
                "region": region,
                "kpi_id": kpi_id,
                "actual": actual,
                "expected": expected,
                "delta": delta,
                "delta_pct": delta_pct,
                "z_score": z_score,
                "material": bool(material),
                "impact_score": round(impact, 1),
                "baseline_method": "28-day governed baseline",
                "as_of": latest_date,
            }
        )

    result = pd.DataFrame(rows)
    result["priority_score"] = result["impact_score"] * np.where(result["material"], 1.0, 0.35)
    result["priority_rank"] = result.groupby("region")["priority_score"].rank(method="dense", ascending=False).astype(int)
    result["priority"] = np.select(
        [result["material"] & result["impact_score"].ge(75), result["material"]],
        ["P1 — immediate review", "P2 — scheduled review"],
        default="P3 — monitor",
    )
    return result.sort_values(["material", "priority_score"], ascending=[False, False]).reset_index(drop=True)
