"""Source loading, reconciliation, enrichment, and freshness reporting."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.data_generator import AS_OF, REGIONS, generate_synthetic_data


@dataclass(frozen=True)
class DataBundle:
    """Reconciled source data and quality context used by every analysis stage."""

    transactions: pd.DataFrame
    kyc: pd.DataFrame
    cases: pd.DataFrame
    enriched: pd.DataFrame
    quality: pd.DataFrame
    source_freshness: pd.DataFrame
    as_of: pd.Timestamp


def _load_metadata(path: Path, as_of: pd.Timestamp) -> pd.DataFrame:
    metadata = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for source, values in metadata["sources"].items():
        refreshed = pd.Timestamp(values["last_refresh"])
        age_hours = (as_of - refreshed).total_seconds() / 3600
        sla = float(values["expected_refresh_sla_hours"])
        rows.append(
            {
                "source": source,
                "last_refresh": refreshed,
                "age_hours": round(age_hours, 2),
                "sla_hours": sla,
                "status": "Fresh" if age_hours <= sla else "Stale",
                "row_count": int(values["row_count"]),
            }
        )
    return pd.DataFrame(rows)


def load_data(project_root: str | Path, force_regenerate: bool = False) -> DataBundle:
    """Load synthetic sources, reconcile KYC, and derive governed data flags."""

    root = Path(project_root)
    generate_synthetic_data(root, force=force_regenerate)
    raw = root / "data" / "raw"

    tx = pd.read_csv(raw / "transactions.csv", parse_dates=["timestamp"])
    kyc = pd.read_csv(raw / "kyc.csv", parse_dates=["account_open_date", "kyc_updated_at"])
    cases = pd.read_csv(raw / "cases.csv", parse_dates=["opened_at", "sla_due_at"])
    for frame, columns in ((tx, ["timestamp"]), (kyc, ["kyc_updated_at"]), (cases, ["opened_at", "sla_due_at"])):
        for column in columns:
            frame[column] = pd.to_datetime(frame[column], utc=True)

    quality_rows: list[dict] = []

    def add_check(check: str, severity: str, affected: int, detail: str) -> None:
        quality_rows.append(
            {
                "check": check,
                "severity": severity,
                "affected_rows": int(affected),
                "status": "Pass" if affected == 0 else ("Warning" if severity == "warning" else "Fail"),
                "detail": detail,
            }
        )

    add_check("Unique transaction IDs", "critical", int(tx["transaction_id"].duplicated().sum()), "Duplicate events are rejected.")
    add_check("Positive transaction amount", "critical", int((tx["amount_inr"] <= 0).sum()), "Zero or negative values are rejected.")
    add_check("Known region", "critical", int((~tx["region"].isin(REGIONS)).sum()), "Unknown regions are quarantined.")
    unmatched = int((~tx["account_id"].isin(kyc["account_id"])).sum())
    add_check("Account-to-KYC match", "warning", unmatched, "Unmatched events are retained with a quality flag.")
    future_events = int((tx["timestamp"] > AS_OF).sum() + (cases["opened_at"] > AS_OF).sum())
    add_check("No future source events", "critical", future_events, "Events after the analytical as-of time are rejected.")

    enriched = tx.merge(kyc, on="account_id", how="left", validate="many_to_one", indicator=True)
    enriched["kyc_match"] = enriched["_merge"].eq("both")
    enriched.drop(columns=["_merge"], inplace=True)
    enriched["kyc_age_hours"] = (AS_OF - enriched["kyc_updated_at"]).dt.total_seconds() / 3600
    enriched["kyc_fresh"] = enriched["kyc_age_hours"].le(30)
    enriched["mapping_complete"] = enriched[["phone_hash", "address_hash"]].fillna("").ne("").any(axis=1)
    enriched["account_age_days"] = (AS_OF.normalize().tz_localize(None) - enriched["account_open_date"]).dt.days
    enriched["account_age_band"] = pd.cut(
        enriched["account_age_days"],
        bins=[-1, 30, 90, 365, 100_000],
        labels=["0–30 days", "31–90 days", "91–365 days", "365+ days"],
    ).astype(str)
    enriched["is_cash"] = enriched["transaction_type"].isin(["CASH_DEPOSIT", "CASH_WITHDRAWAL"])
    enriched["is_near_threshold"] = enriched["is_cash"] & enriched["amount_inr"].between(800_000, 999_999.99)
    enriched["date"] = enriched["timestamp"].dt.floor("D")

    freshness = _load_metadata(raw / "source_metadata.json", AS_OF)
    return DataBundle(tx, kyc, cases, enriched, pd.DataFrame(quality_rows), freshness, AS_OF)


def quality_score(bundle: DataBundle) -> float:
    """Return a zero-to-one score from critical failures and source freshness."""

    critical_failures = int(
        bundle.quality.loc[bundle.quality["severity"].eq("critical"), "affected_rows"].sum()
    )
    freshness_ratio = float(bundle.source_freshness["status"].eq("Fresh").mean())
    return round(max(0.0, 1.0 - min(1.0, critical_failures / 10)) * freshness_ratio, 3)

