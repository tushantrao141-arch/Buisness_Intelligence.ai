"""Structured, access-checked evidence packets and sanitized LLM payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.analytics import AnalysisResult
from src.data import DataBundle
from src.narrative import evidence_items, recommended_action_ids
from src.schemas import ConfigBundle, UserEntitlement
from src.security import enforce_access, mask_identifier


FINDING_KPI = {
    "Connected pattern": "linked_pattern_exposure",
    "Evidence gap": "near_threshold_value_ratio",
    "Alternative hypothesis": "near_threshold_value_ratio",
    "Sparse history": "near_threshold_value_ratio",
}


def build_evidence_packet(
    data: DataBundle,
    analysis: AnalysisResult,
    bundle: ConfigBundle,
    user: UserEntitlement,
    region: str,
    finding_id: str,
) -> dict[str, Any]:
    """Build a packet only after entitlement succeeds.

    Access enforcement is deliberately the first executable step so restricted
    rows cannot enter filtering, evidence construction, or an LLM payload.
    """

    enforce_access(user, region, detail=False)
    matching = analysis.findings.loc[
        analysis.findings["finding_id"].eq(finding_id) & analysis.findings["region"].eq(region)
    ]
    if matching.empty:
        raise KeyError(f"Finding {finding_id!r} is not available in the authorised {region} scope")
    finding = matching.iloc[0]
    kpi_id = FINDING_KPI.get(str(finding["finding_type"]), "linked_pattern_exposure")
    contract = next(kpi for kpi in bundle.kpis if kpi.id == kpi_id)
    movement = analysis.movements.loc[
        analysis.movements["region"].eq(region) & analysis.movements["kpi_id"].eq(kpi_id)
    ].iloc[0]
    driver_rows = analysis.drivers.loc[
        analysis.drivers["region"].eq(region) & analysis.drivers["kpi_id"].eq(kpi_id)
    ].head(8)
    account_ids = list(finding["account_ids"])
    related = data.enriched.loc[data.enriched["account_id"].isin(account_ids)]
    stale_accounts = int(related.loc[~related["kyc_fresh"], "account_id"].nunique())
    incomplete_accounts = int(related.loc[~related["mapping_complete"], "account_id"].nunique())
    action_ids = recommended_action_ids(finding, user, bundle)
    action_by_id = {action.id: action for action in bundle.actions}
    entity_scope: dict[str, Any]
    if user.can_view_entity_detail:
        entity_scope = {
            "detail_level": "masked entity detail",
            "masked_accounts": [mask_identifier(account, bundle.settings.security.mask_account_suffix_length) for account in account_ids],
            "account_count": len(account_ids),
        }
    else:
        entity_scope = {"detail_level": "aggregate only", "account_count": len(account_ids)}

    return {
        "packet_version": "1.0",
        "packet_id": f"EP-{finding_id}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "persona": {"user_id": user.id, "role": user.role, "region_scope": region},
        "finding": {
            "finding_id": finding_id,
            "title": str(finding["title"]),
            "type": str(finding["finding_type"]),
            "decision": str(finding["decision"]),
            "summary": str(finding["summary"]),
        },
        "kpi": {
            "id": kpi_id,
            "name": contract.name,
            "definition": contract.description,
            "unit": contract.unit,
            "grain": contract.grain,
            "owner": contract.owner,
            "actual": float(movement["actual"]),
            "expected": float(movement["expected"]),
            "change": float(movement["delta"]),
            "change_percent": float(movement["delta_pct"]),
            "priority": str(movement["priority"]),
        },
        "drivers": [
            {
                "driver": str(row.driver),
                "contribution": float(row.contribution),
                "contribution_percent": float(row.contribution_pct),
                "evidence_id": f"D{index:02d}",
            }
            for index, row in enumerate(driver_rows.itertuples(index=False), 1)
        ],
        "driver_reconciliation": {
            "movement_total": float(driver_rows["movement_total"].iloc[0]) if not driver_rows.empty else 0.0,
            "explained_total": float(driver_rows["explained_total"].iloc[0]) if not driver_rows.empty else 0.0,
            "unexplained": float(driver_rows["unexplained"].iloc[0]) if not driver_rows.empty else 0.0,
        },
        "source_freshness": [
            {
                "source": str(row.source),
                "last_refresh": pd.Timestamp(row.last_refresh).isoformat(),
                "age_hours": float(row.age_hours),
                "sla_hours": float(row.sla_hours),
                "status": str(row.status),
            }
            for row in data.source_freshness.itertuples(index=False)
        ],
        "missing_data": {"stale_kyc_accounts": stale_accounts, "incomplete_mapping_accounts": incomplete_accounts},
        "analytical_method": str(finding["method"]),
        "confidence": {
            "evidence_confidence": float(finding["confidence"]),
            "pattern_strength": float(finding["pattern_strength"]),
            "abstention_threshold": float(bundle.settings.analysis.abstention_confidence_below),
        },
        "alternative_hypothesis": str(finding["alternative_hypothesis"]),
        "evidence": evidence_items(finding),
        "entity_scope": entity_scope,
        "permitted_actions": [
            {
                "action_id": action_id,
                "action": action_by_id[action_id].action,
                "owner": action_by_id[action_id].owner,
                "monitoring_kpi": action_by_id[action_id].monitoring_kpi,
            }
            for action_id in action_ids
        ],
        "guardrails": {
            "synthetic_data_only": bundle.settings.project.synthetic_data_only,
            "raw_identifiers_present": False,
            "quantitative_values_computed_by_llm": False,
            "high_impact_action_automatic": False,
        },
    }


def llm_payload(packet: dict[str, Any]) -> dict[str, Any]:
    """Return the complete already-sanitized packet; nothing else may reach the LLM."""
    if packet.get("guardrails", {}).get("raw_identifiers_present") is not False:
        raise ValueError("Evidence packet failed the raw-identifier guardrail")
    return packet

