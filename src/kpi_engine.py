"""Pure, hand-verifiable implementations of the five governed KPIs."""

from __future__ import annotations

import pandas as pd


CASH_TYPES = {"CASH_DEPOSIT", "CASH_WITHDRAWAL"}
ACTIVE_CASE_STATUSES = {"OPEN", "IN_REVIEW"}
POSITIVE_DISPOSITIONS = {"CONFIRMED", "ESCALATED"}


def near_threshold_value_ratio(transactions: pd.DataFrame, threshold_inr: float = 1_000_000, lower_ratio: float = 0.80) -> float:
    """Qualifying near-threshold cash value / all relevant cash value × 100."""
    cash = transactions.loc[transactions["transaction_type"].isin(CASH_TYPES)]
    total = float(cash["amount_inr"].sum())
    if total <= 0:
        return 0.0
    lower = threshold_inr * lower_ratio
    near = cash.loc[cash["amount_inr"].ge(lower) & cash["amount_inr"].lt(threshold_inr)]
    return float(near["amount_inr"].sum() / total * 100)


def linked_pattern_exposure(transactions: pd.DataFrame, qualifying_transaction_ids: set[str] | list[str]) -> float:
    """Sum each unique qualifying transaction exactly once."""
    qualifying = set(qualifying_transaction_ids)
    unique = transactions.drop_duplicates("transaction_id")
    return float(unique.loc[unique["transaction_id"].isin(qualifying), "amount_inr"].sum())


def high_risk_cluster_count(clusters: pd.DataFrame, review_score_threshold: float = 60) -> int:
    """Count distinct clusters at or above the transparent review-score threshold."""
    if clusters.empty:
        return 0
    qualifying = clusters.loc[clusters["review_score"].ge(review_score_threshold)]
    return int(qualifying["cluster_id"].nunique())


def alert_investigation_yield(cases: pd.DataFrame) -> float:
    """Positive completed investigations / all completed investigations × 100."""
    closed = cases.loc[cases["status"].astype(str).str.startswith("CLOSED")]
    if closed.empty:
        return 0.0
    positive = closed["final_disposition"].isin(POSITIVE_DISPOSITIONS)
    return float(positive.sum() / len(closed) * 100)


def case_sla_risk(cases: pd.DataFrame, as_of: pd.Timestamp, horizon_hours: int = 24) -> int:
    """Active cases due from as-of through the configured horizon, inclusive."""
    as_of_utc = pd.Timestamp(as_of)
    if as_of_utc.tzinfo is None:
        as_of_utc = as_of_utc.tz_localize("UTC")
    due = pd.to_datetime(cases["sla_due_at"], utc=True)
    at_risk = cases["status"].isin(ACTIVE_CASE_STATUSES) & due.ge(as_of_utc) & due.le(as_of_utc + pd.Timedelta(hours=horizon_hours))
    return int(at_risk.sum())
