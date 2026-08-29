"""Behavioral, temporal, and account-level feature derivation layer."""

from __future__ import annotations

import pandas as pd
import numpy as np
from src.data_generator import AS_OF


def derive_behavioral_features(tx: pd.DataFrame, kyc: pd.DataFrame, as_of: pd.Timestamp = AS_OF) -> pd.DataFrame:
    """Derive rich, explainable behavioral and temporal risk signals."""
    enriched = tx.merge(kyc, on="account_id", how="left", validate="many_to_one", indicator=True)
    enriched["kyc_match"] = enriched["_merge"].eq("both")
    enriched.drop(columns=["_merge"], inplace=True)

    # KYC Freshness & Mapping
    enriched["kyc_age_hours"] = (as_of - enriched["kyc_updated_at"]).dt.total_seconds() / 3600
    enriched["kyc_fresh"] = enriched["kyc_age_hours"].le(30 * 24)
    enriched["mapping_complete"] = enriched[["phone_hash", "address_hash"]].fillna("").ne("").any(axis=1)

    # Account Age Band
    enriched["account_age_days"] = (as_of.normalize().tz_localize(None) - enriched["account_open_date"]).dt.days
    enriched["account_age_band"] = pd.cut(
        enriched["account_age_days"],
        bins=[-1, 30, 90, 365, 100_000],
        labels=["0–30 days", "31–90 days", "91–365 days", "365+ days"],
    ).astype(str)

    # Cash & Threshold Indicators
    enriched["is_cash"] = enriched["transaction_type"].isin(["CASH_DEPOSIT", "CASH_WITHDRAWAL"])
    enriched["is_near_threshold"] = enriched["is_cash"] & enriched["amount_inr"].between(800_000, 999_999.99)
    enriched["date"] = enriched["timestamp"].dt.floor("D")

    # Velocity by account (count in past 7 days per account)
    account_7d_counts = enriched.groupby("account_id").size()
    enriched["velocity_7d"] = enriched["account_id"].map(account_7d_counts).fillna(1).astype(int)

    # Distinct branches used by account (branch dispersion)
    account_branches = enriched.groupby("account_id")["branch_id"].nunique()
    enriched["branch_hop_3d"] = enriched["account_id"].map(account_branches).fillna(1).astype(int)

    # Turnover deviation ratio
    monthly_actual = enriched.groupby("account_id")["amount_inr"].transform("sum") / 3.0
    expected_turnover = enriched["expected_monthly_turnover_inr"].replace(0, np.nan)
    enriched["turnover_deviation_ratio"] = (monthly_actual / expected_turnover).fillna(1.0).round(2)

    return enriched
