"""Ranked driver contributions, unexplained residual, and exact reconciliation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data import DataBundle
from src.graph_engine import RelationshipResult


def calculate_drivers(data: DataBundle, relationships: RelationshipResult) -> pd.DataFrame:
    """Create leaf-segment contributions that reconcile exactly to KPI movement."""
    tx = data.enriched.merge(
        relationships.transaction_clusters[["transaction_id", "cluster_id", "qualifies"]],
        on="transaction_id",
        how="left",
    )
    tx["qualifies"] = tx["qualifies"].eq(True)
    tx["cluster_label"] = tx["cluster_id"].fillna("No qualifying cluster")
    latest = data.as_of.floor("D")
    current_dates = pd.date_range(latest - pd.Timedelta(days=6), latest, freq="D", tz="UTC")
    baseline_dates = pd.date_range(latest - pd.Timedelta(days=35), latest - pd.Timedelta(days=8), freq="D", tz="UTC")
    leaf_columns = ["region", "branch_id", "channel", "account_age_band", "business_type", "cluster_label"]
    rows: list[dict] = []

    def leaf_name(values: tuple) -> str:
        labels = ["Region", "Branch", "Channel", "Account age", "Customer", "Cluster"]
        return " · ".join(f"{label}: {value}" for label, value in zip(labels, values))

    def append_reconciled(region: str, kpi_id: str, current: pd.Series, expected: pd.Series) -> None:
        keys = current.index.union(expected.index)
        actual_total = float(current.reindex(keys, fill_value=0).sum())
        expected_total = float(expected.reindex(keys, fill_value=0).sum())
        movement = actual_total - expected_total
        contributions = current.reindex(keys, fill_value=0) - expected.reindex(keys, fill_value=0)
        explained = float(contributions.sum())
        unexplained = float(movement - explained)
        for key, contribution in contributions.items():
            values = key if isinstance(key, tuple) else (key,)
            rows.append(
                {
                    "region": region,
                    "kpi_id": kpi_id,
                    "dimension": "reconciled_leaf" if len(values) > 1 else "cluster_id",
                    "value": " | ".join(map(str, values)),
                    "driver": leaf_name(values) if len(values) > 1 else f"Cluster: {values[0]}",
                    "actual": float(current.get(key, 0.0)),
                    "expected": float(expected.get(key, 0.0)),
                    "contribution": float(contribution),
                    "contribution_pct": float(contribution / movement * 100) if abs(movement) > 1e-12 else 0.0,
                    "movement_total": movement,
                    "explained_total": explained,
                    "unexplained": unexplained,
                    "reconciles": abs(unexplained) < 1e-8,
                }
            )

    for region in ["ALL", "NORTH", "SOUTH", "EAST", "WEST"]:
        scope = tx if region == "ALL" else tx.loc[tx["region"].eq(region)]
        cash_totals = scope.loc[scope["is_cash"]].groupby("date")["amount_inr"].sum()
        near = scope.loc[scope["is_near_threshold"]].copy()
        if near.empty:
            current_near = pd.Series(dtype=float)
            baseline_near = pd.Series(dtype=float)
        else:
            near_by_day = near.groupby(["date", *leaf_columns], observed=True)["amount_inr"].sum()
            shares = near_by_day.reset_index(name="near_value")
            shares["daily_share_pp"] = shares["near_value"] / shares["date"].map(cash_totals).replace(0, np.nan) * 100
            current_near = shares.loc[shares["date"].isin(current_dates)].groupby(leaf_columns, observed=True)["daily_share_pp"].sum() / len(current_dates)
            baseline_near = shares.loc[shares["date"].isin(baseline_dates)].groupby(leaf_columns, observed=True)["daily_share_pp"].sum() / len(baseline_dates)
        append_reconciled(region, "near_threshold_value_ratio", current_near, baseline_near)

        linked = scope.loc[scope["qualifies"]].copy()
        current_linked = linked.loc[linked["date"].isin(current_dates)].groupby(leaf_columns, observed=True)["amount_inr"].sum()
        baseline_linked = linked.loc[linked["date"].isin(baseline_dates)].groupby(leaf_columns, observed=True)["amount_inr"].sum() / 4
        append_reconciled(region, "linked_pattern_exposure", current_linked, baseline_linked)

        active = linked[["date", "cluster_id"]].dropna().drop_duplicates()
        current_clusters = active.loc[active["date"].eq(latest)].groupby("cluster_id").size().astype(float)
        baseline_clusters = active.loc[active["date"].isin(baseline_dates)].groupby("cluster_id").size().astype(float) / len(baseline_dates)
        append_reconciled(region, "high_risk_cluster_count", current_clusters, baseline_clusters)

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values("contribution", key=lambda series: series.abs(), ascending=False).reset_index(drop=True)
