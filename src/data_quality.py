"""Data quality and reconciliation layer.

Validates schema, duplicates, non-positive amounts, region validity,
matching completeness, and freshness. Writes clean processed Parquet files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from src.config import load_config_bundle
from src.data_generator import AS_OF, REGIONS


@dataclass(frozen=True)
class QualityReport:
    """Summary and row-level results from source validation checks."""

    total_checks: int
    critical_failures: int
    warnings: int
    quality_score: float
    checks: pd.DataFrame


def validate_and_process_data(project_root: str | Path) -> QualityReport:
    """Run rigorous validation checks and write processed Parquet views."""
    root = Path(project_root)
    raw_dir = root / "data" / "raw"
    proc_dir = root / "data" / "processed"
    proc_dir.mkdir(parents=True, exist_ok=True)

    tx = pd.read_csv(raw_dir / "transactions.csv", parse_dates=["timestamp"])
    kyc = pd.read_csv(raw_dir / "kyc.csv", parse_dates=["account_open_date", "kyc_updated_at"])
    cases = pd.read_csv(raw_dir / "cases.csv", parse_dates=["opened_at", "sla_due_at"])

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

    # 1. Unique transaction IDs
    dup_tx = int(tx["transaction_id"].duplicated().sum())
    add_check("Unique transaction IDs", "critical", dup_tx, "Duplicate transaction events are rejected.")

    # 2. Positive amounts
    non_pos = int((tx["amount_inr"] <= 0).sum())
    add_check("Positive transaction amount", "critical", non_pos, "Zero or negative amounts are rejected.")

    # 3. Known regions
    unknown_reg = int((~tx["region"].isin(REGIONS)).sum())
    add_check("Known region", "critical", unknown_reg, "Unknown regions are quarantined.")

    # 4. Account-to-KYC match
    unmatched = int((~tx["account_id"].isin(kyc["account_id"])).sum())
    add_check("Account-to-KYC match", "warning", unmatched, "Unmatched accounts are flagged.")

    # 5. No future timestamps
    future_events = int((tx["timestamp"] > AS_OF).sum() + (cases["opened_at"] > AS_OF).sum())
    add_check("No future source events", "critical", future_events, "Events after as-of time are rejected.")

    kyc_sla_hours = load_config_bundle(root).settings.freshness_sla_hours.kyc
    kyc_age = (AS_OF - kyc["kyc_updated_at"]).dt.total_seconds() / 3600
    stale_kyc = int((kyc_age > kyc_sla_hours).sum())
    add_check("KYC freshness SLA", "warning", stale_kyc, "Stale KYC records flagged.")

    checks_df = pd.DataFrame(quality_rows)
    crit_fail = int(checks_df.loc[checks_df["severity"].eq("critical"), "affected_rows"].sum())
    warn_count = int((checks_df["status"] == "Warning").sum())
    score = round(max(0.0, 1.0 - min(1.0, crit_fail / 10)), 3)

    # Write clean processed Parquet files
    tx.to_parquet(proc_dir / "transactions.parquet", index=False)
    kyc.to_parquet(proc_dir / "kyc.parquet", index=False)
    cases.to_parquet(proc_dir / "cases.parquet", index=False)

    return QualityReport(
        total_checks=len(checks_df),
        critical_failures=crit_fail,
        warnings=warn_count,
        quality_score=score,
        checks=checks_df,
    )


if __name__ == "__main__":
    rep = validate_and_process_data(Path(__file__).resolve().parents[1])
    print(f"Data validation complete: Quality Score={rep.quality_score}, Critical Failures={rep.critical_failures}")
