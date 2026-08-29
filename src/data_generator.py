"""Deterministic synthetic data for the SilentSignal demonstration.

Ground-truth labels are written separately and are never consumed by the
analytical pipeline. They exist only for the held-out evaluation module.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


AS_OF = pd.Timestamp("2026-08-20T12:00:00Z")
REGIONS = ("NORTH", "SOUTH", "EAST", "WEST")
BRANCHES = {region: [f"{region[0]}{index:02d}" for index in range(1, 5)] for region in REGIONS}


def _utc_text(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_synthetic_data(project_root: str | Path, force: bool = False) -> dict[str, int]:
    """Generate stable heterogeneous sources and isolated evaluation labels."""

    root = Path(project_root)
    raw_dir = root / "data" / "raw"
    truth_dir = root / "data" / "ground_truth"
    raw_dir.mkdir(parents=True, exist_ok=True)
    truth_dir.mkdir(parents=True, exist_ok=True)

    required = [raw_dir / "transactions.csv", raw_dir / "kyc.csv", raw_dir / "cases.csv"]
    if not force and all(path.exists() for path in required):
        return {
            "transactions": len(pd.read_csv(required[0])),
            "kyc": len(pd.read_csv(required[1])),
            "cases": len(pd.read_csv(required[2])),
        }

    rng = np.random.default_rng(42)
    kyc_rows: list[dict] = []
    account_by_region: dict[str, list[str]] = {region: [] for region in REGIONS}
    business_types = ("RETAIL", "WHOLESALE", "PROFESSIONAL", "CASH_INTENSIVE")

    for region in REGIONS:
        for index in range(1, 81):
            account_id = f"{region[0]}A{index:04d}"
            account_by_region[region].append(account_id)
            business_type = rng.choice(business_types, p=[0.48, 0.22, 0.20, 0.10])
            kyc_rows.append(
                {
                    "customer_id": f"C{region[0]}{index:04d}",
                    "account_id": account_id,
                    "business_type": business_type,
                    "risk_tier": rng.choice(["LOW", "MEDIUM", "HIGH"], p=[0.60, 0.30, 0.10]),
                    "expected_monthly_turnover_inr": int(rng.uniform(1_500_000, 18_000_000)),
                    "account_open_date": (AS_OF - pd.Timedelta(days=int(rng.integers(90, 1200)))).date(),
                    "phone_hash": f"ph_{region.lower()}_{index:04d}",
                    "address_hash": f"ad_{region.lower()}_{index:04d}",
                    "kyc_updated_at": AS_OF - pd.Timedelta(hours=int(rng.integers(2, 300))),
                }
            )

    # S1: eight new WEST accounts share identifiers and beneficiaries.
    s1_accounts = [f"W_SIG_{index:02d}" for index in range(1, 9)]
    for index, account_id in enumerate(s1_accounts, 1):
        account_by_region["WEST"].append(account_id)
        kyc_rows.append(
            {
                "customer_id": f"CW_SIG_{index:02d}",
                "account_id": account_id,
                "business_type": "RETAIL",
                "risk_tier": "HIGH" if index <= 3 else "MEDIUM",
                "expected_monthly_turnover_inr": 2_200_000,
                "account_open_date": (AS_OF - pd.Timedelta(days=18 + index)).date(),
                "phone_hash": f"ph_signal_{(index - 1) // 2}",
                "address_hash": "ad_signal_shared",
                "kyc_updated_at": AS_OF - pd.Timedelta(hours=8 + index),
            }
        )

    # S2: a fresh, documented cash-intensive seasonal account without relationships.
    s2_account = "E_SEASONAL_01"
    account_by_region["EAST"].append(s2_account)
    kyc_rows.append(
        {
            "customer_id": "CE_SEASONAL_01",
            "account_id": s2_account,
            "business_type": "CASH_INTENSIVE",
            "risk_tier": "LOW",
            "expected_monthly_turnover_inr": 24_000_000,
            "account_open_date": (AS_OF - pd.Timedelta(days=780)).date(),
            "phone_hash": "ph_seasonal_unique",
            "address_hash": "ad_seasonal_unique",
            "kyc_updated_at": AS_OF - pd.Timedelta(hours=6),
        }
    )

    # S3: near-threshold NORTH accounts with stale KYC and incomplete mapping.
    s3_accounts = [f"N_GAP_{index:02d}" for index in range(1, 5)]
    for index, account_id in enumerate(s3_accounts, 1):
        account_by_region["NORTH"].append(account_id)
        kyc_rows.append(
            {
                "customer_id": f"CN_GAP_{index:02d}",
                "account_id": account_id,
                "business_type": "PROFESSIONAL",
                "risk_tier": "MEDIUM",
                "expected_monthly_turnover_inr": 4_500_000,
                "account_open_date": (AS_OF - pd.Timedelta(days=220 + index)).date(),
                "phone_hash": "",
                "address_hash": "",
                "kyc_updated_at": AS_OF - pd.Timedelta(days=75 + index),
            }
        )

    # S4: a channel with only fourteen days of history.
    s4_accounts = [f"S_NEW_{index:02d}" for index in range(1, 7)]
    for index, account_id in enumerate(s4_accounts, 1):
        account_by_region["SOUTH"].append(account_id)
        kyc_rows.append(
            {
                "customer_id": f"CS_NEW_{index:02d}",
                "account_id": account_id,
                "business_type": "RETAIL",
                "risk_tier": "LOW",
                "expected_monthly_turnover_inr": 5_000_000,
                "account_open_date": (AS_OF - pd.Timedelta(days=60 + index)).date(),
                "phone_hash": f"ph_new_{index:02d}",
                "address_hash": f"ad_new_{index:02d}",
                "kyc_updated_at": AS_OF - pd.Timedelta(hours=12 + index),
            }
        )

    kyc = pd.DataFrame(kyc_rows)
    kyc["account_open_date"] = pd.to_datetime(kyc["account_open_date"]).dt.strftime("%Y-%m-%d")
    kyc["kyc_updated_at"] = _utc_text(kyc["kyc_updated_at"])

    transactions: list[dict] = []
    transaction_number = 1

    def add_transaction(
        timestamp: pd.Timestamp,
        account_id: str,
        amount: float,
        branch_id: str,
        region: str,
        channel: str,
        transaction_type: str,
        beneficiary_hash: str = "",
    ) -> None:
        nonlocal transaction_number
        if timestamp > AS_OF:
            timestamp = AS_OF - pd.Timedelta(minutes=(transaction_number % 55) + 1)
        transactions.append(
            {
                "transaction_id": f"TX{transaction_number:07d}",
                "timestamp": timestamp,
                "account_id": account_id,
                "amount_inr": round(float(amount), 2),
                "branch_id": branch_id,
                "region": region,
                "channel": channel,
                "transaction_type": transaction_type,
                "beneficiary_hash": beneficiary_hash,
            }
        )
        transaction_number += 1

    # Ninety days of ordinary history.
    for days_ago in range(89, -1, -1):
        day = (AS_OF - pd.Timedelta(days=days_ago)).normalize()
        for region in REGIONS:
            ordinary_accounts = [account for account in account_by_region[region] if "_" not in account]
            for _ in range(46):
                account_id = str(rng.choice(ordinary_accounts))
                transaction_type = str(
                    rng.choice(["CASH_DEPOSIT", "CASH_WITHDRAWAL", "TRANSFER"], p=[0.42, 0.18, 0.40])
                )
                channel = str(rng.choice(["BRANCH_CASH", "ATM", "ONLINE"], p=[0.47, 0.15, 0.38]))
                amount = min(float(rng.lognormal(mean=12.0, sigma=0.78)), 1_350_000)
                add_transaction(
                    day + pd.Timedelta(minutes=int(rng.integers(30, 1380))),
                    account_id,
                    amount,
                    str(rng.choice(BRANCHES[region])),
                    region,
                    channel,
                    transaction_type,
                    f"ben_{region.lower()}_{int(rng.integers(1, 350)):04d}" if transaction_type == "TRANSFER" else "",
                )

    for days_ago in range(13, -1, -1):
        day = (AS_OF - pd.Timedelta(days=days_ago)).normalize()
        for index, account_id in enumerate(s1_accounts):
            for event in range(2):
                add_transaction(
                    day + pd.Timedelta(hours=8 + (index % 6), minutes=event * 19),
                    account_id,
                    835_000 + ((days_ago * 17 + index * 11 + event * 7) % 145) * 1_000,
                    BRANCHES["WEST"][(index + event) % 4],
                    "WEST",
                    "BRANCH_CASH",
                    "CASH_DEPOSIT",
                    "ben_signal_shared",
                )

    for days_ago in range(6, -1, -1):
        day = (AS_OF - pd.Timedelta(days=days_ago)).normalize()
        for event in range(3):
            add_transaction(
                day + pd.Timedelta(hours=9 + event * 3),
                s2_account,
                620_000 + days_ago * 8_000 + event * 25_000,
                BRANCHES["EAST"][1],
                "EAST",
                "BRANCH_CASH",
                "CASH_DEPOSIT",
                "",
            )
        for index, account_id in enumerate(s3_accounts):
            add_transaction(
                day + pd.Timedelta(hours=10 + index),
                account_id,
                870_000 + ((days_ago + index) % 7) * 14_000,
                BRANCHES["NORTH"][index],
                "NORTH",
                "BRANCH_CASH",
                "CASH_DEPOSIT",
                "",
            )

    for days_ago in range(13, -1, -1):
        day = (AS_OF - pd.Timedelta(days=days_ago)).normalize()
        for index, account_id in enumerate(s4_accounts):
            add_transaction(
                day + pd.Timedelta(hours=7 + index),
                account_id,
                180_000 + ((days_ago + index) % 9) * 18_000,
                BRANCHES["SOUTH"][index % 4],
                "SOUTH",
                "NEW_DEPOSIT",
                "CASH_DEPOSIT",
                "",
            )

    tx = pd.DataFrame(transactions)
    tx["timestamp"] = _utc_text(tx["timestamp"])

    account_customer = {row["account_id"]: row["customer_id"] for row in kyc_rows}

    case_rows: list[dict] = []
    for index in range(1, 101):
        region = REGIONS[(index - 1) % 4]
        region_accounts = [a for a in account_by_region[region] if "_" not in a]
        case_account = str(rng.choice(region_accounts))
        case_customer = account_customer.get(case_account, "")
        opened = AS_OF - pd.Timedelta(days=int(rng.integers(3, 80)), hours=int(rng.integers(0, 20)))
        confirmed = index % 5 in (0, 1)
        case_rows.append(
            {
                "case_id": f"CASE{index:04d}",
                "account_id": case_account,
                "customer_id": case_customer,
                "cluster_id": "",
                "status": "CLOSED_CONFIRMED" if confirmed else "CLOSED_CLEARED",
                "assigned_investigator": f"{region.lower()}_team_{index % 3 + 1}",
                "region": region,
                "opened_at": opened,
                "sla_due_at": opened + pd.Timedelta(days=5),
                "final_disposition": "CONFIRMED" if confirmed else "CLEARED",
            }
        )

    for index in range(101, 125):
        region = "WEST" if index < 116 else REGIONS[index % 4]
        if region == "WEST" and index < 108:
            case_account = str(rng.choice(s1_accounts))
            cluster = "SIG-WEST-001"
        else:
            region_accounts = [a for a in account_by_region[region] if "_" not in a]
            case_account = str(rng.choice(region_accounts))
            cluster = ""
        case_customer = account_customer.get(case_account, "")
        opened = AS_OF - pd.Timedelta(days=int(rng.integers(1, 6)))
        hours_to_due = int(rng.integers(2, 22)) if region == "WEST" else int(rng.integers(30, 80))
        case_rows.append(
            {
                "case_id": f"CASE{index:04d}",
                "account_id": case_account,
                "customer_id": case_customer,
                "cluster_id": cluster,
                "status": "IN_REVIEW" if index % 2 else "OPEN",
                "assigned_investigator": f"{region.lower()}_team_{index % 3 + 1}",
                "region": region,
                "opened_at": opened,
                "sla_due_at": AS_OF + pd.Timedelta(hours=hours_to_due),
                "final_disposition": "",
            }
        )

    cases = pd.DataFrame(case_rows)
    cases["opened_at"] = _utc_text(cases["opened_at"])
    cases["sla_due_at"] = _utc_text(cases["sla_due_at"])

    tx.to_csv(raw_dir / "transactions.csv", index=False)
    kyc.to_csv(raw_dir / "kyc.csv", index=False)
    cases.to_csv(raw_dir / "cases.csv", index=False)

    truth = pd.DataFrame(
        [
            {"scenario_id": "S1", "name": "Strong connected pattern", "region": "WEST", "expected_outcome": "ALERT", "entity_ids": json.dumps(s1_accounts), "expected_driver_dimensions": json.dumps(["region", "branch_id", "account_age_band", "cluster_label"]), "description": "Connected new accounts with repeated near-threshold cash activity."},
            {"scenario_id": "S2", "name": "Legitimate seasonal activity", "region": "EAST", "expected_outcome": "MONITOR", "entity_ids": json.dumps([s2_account]), "expected_driver_dimensions": json.dumps(["business_type"]), "description": "Fresh KYC and documented turnover support a seasonal alternative."},
            {"scenario_id": "S3", "name": "Insufficient evidence", "region": "NORTH", "expected_outcome": "ABSTAIN", "entity_ids": json.dumps(s3_accounts), "expected_driver_dimensions": json.dumps(["kyc_fresh", "mapping_complete"]), "description": "Stale KYC and missing mappings require more information."},
            {"scenario_id": "S4", "name": "Sparse-history channel", "region": "SOUTH", "expected_outcome": "PEER_BASED", "entity_ids": json.dumps(s4_accounts), "expected_driver_dimensions": json.dumps(["channel"]), "description": "NEW_DEPOSIT has only fourteen days of history."},
            {"scenario_id": "S5", "name": "Unauthorised region", "region": "NORTH", "expected_outcome": "ACCESS_DENIED", "entity_ids": json.dumps([]), "expected_driver_dimensions": json.dumps([]), "description": "A WEST investigator requests NORTH details."},
        ]
    )
    truth.to_csv(truth_dir / "events.csv", index=False)

    metadata = {
        "schema_version": "1.0.0",
        "generated_at": AS_OF.isoformat(),
        "sources": {
            "transactions": {"last_refresh": (AS_OF - pd.Timedelta(minutes=12)).isoformat(), "expected_refresh_sla_hours": 1, "row_count": len(tx)},
            "kyc": {"last_refresh": (AS_OF - pd.Timedelta(hours=4)).isoformat(), "expected_refresh_sla_hours": 30, "row_count": len(kyc)},
            "cases": {"last_refresh": (AS_OF - pd.Timedelta(hours=2)).isoformat(), "expected_refresh_sla_hours": 6, "row_count": len(cases)},
        },
    }
    (raw_dir / "source_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"transactions": len(tx), "kyc": len(kyc), "cases": len(cases)}
