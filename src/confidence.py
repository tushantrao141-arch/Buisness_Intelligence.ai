"""Evidence quality score, confidence calculation, and abstention gate."""

from __future__ import annotations

import pandas as pd
from src.data import DataBundle, quality_score
from src.graph_engine import RelationshipResult


def build_findings(data: DataBundle, relationships: RelationshipResult) -> pd.DataFrame:
    """Evaluate patterns against transparent confidence criteria and abstention gates."""
    rows: list[dict] = []
    recent_start = data.as_of - pd.Timedelta(days=14)
    recent = data.enriched.loc[data.enriched["timestamp"].ge(recent_start)]

    for cluster in relationships.clusters.loc[relationships.clusters["qualifies"]].itertuples(index=False):
        accounts = list(cluster.account_ids)
        evidence = recent.loc[recent["account_id"].isin(accounts)]
        fresh = float(evidence.groupby("account_id")["kyc_fresh"].max().mean())
        mapped = float(evidence.groupby("account_id")["mapping_complete"].max().mean())
        sample = min(1.0, cluster.near_threshold_count / 16)
        confidence = round(0.30 * fresh + 0.25 * mapped + 0.25 * sample + 0.20 * quality_score(data), 2)
        decision = "ALERT" if confidence >= 0.75 else ("ABSTAIN" if confidence < 0.60 else "MONITOR")
        rows.append(
            {
                "finding_id": cluster.cluster_id,
                "finding_type": "Connected pattern",
                "region": cluster.region,
                "title": f"{cluster.account_count}-account connected cash pattern",
                "decision": decision,
                "confidence": confidence,
                "pattern_strength": round(cluster.risk_score / 100, 2),
                "method": "Transparent relationship graph + governed review score",
                "summary": f"{cluster.account_count} accounts across {cluster.branch_count} branches generated {cluster.near_threshold_count} near-threshold events.",
                "supporting_evidence": f"{cluster.relationship_types}; unique exposure ₹{cluster.exposure_inr:,.0f}.",
                "contradicting_evidence": "No confirmed case disposition is used as proof of wrongdoing.",
                "alternative_hypothesis": "Shared service providers or documented group ownership may explain some links.",
                "requested_information": "Verify ownership, source of funds, and relationship purpose.",
                "account_ids": accounts,
                "cluster_id": cluster.cluster_id,
            }
        )

    # S3: Stale KYC + missing mappings gate -> ABSTAIN
    quality_candidates = recent.loc[recent["is_near_threshold"] & (~recent["kyc_fresh"] | ~recent["mapping_complete"])]
    for region, group in quality_candidates.groupby("region"):
        account_counts = group.groupby("account_id").size()
        accounts = sorted(account_counts.loc[account_counts.ge(3)].index.tolist())
        if len(accounts) < 2:
            continue
        scoped = group.loc[group["account_id"].isin(accounts)]
        fresh = float(scoped.groupby("account_id")["kyc_fresh"].max().mean())
        mapped = float(scoped.groupby("account_id")["mapping_complete"].max().mean())
        confidence = round(0.35 * fresh + 0.25 * mapped + 0.20 + 0.20 * quality_score(data), 2)
        rows.append(
            {
                "finding_id": f"DQ-{region}-001",
                "finding_type": "Evidence gap",
                "region": region,
                "title": "Near-threshold activity with insufficient entity evidence",
                "decision": "ABSTAIN" if confidence < 0.60 else "MONITOR",
                "confidence": confidence,
                "pattern_strength": min(1.0, len(scoped) / 24),
                "method": "Critical evidence-quality gate",
                "summary": f"{len(accounts)} accounts show relevant activity, but KYC or relationship mapping is incomplete.",
                "supporting_evidence": f"{int(scoped['is_near_threshold'].sum())} near-threshold events were observed.",
                "contradicting_evidence": "The available data cannot establish whether the accounts are related.",
                "alternative_hypothesis": "Legitimate activity remains plausible because expected-activity data is stale.",
                "requested_information": "Refresh KYC and complete entity/beneficiary mapping before escalation.",
                "account_ids": accounts,
                "cluster_id": "",
            }
        )

    # S2: Seasonal cash increase within documented profile -> MONITOR
    seasonal = recent.loc[recent["business_type"].eq("CASH_INTENSIVE") & recent["kyc_fresh"]]
    seasonal_totals = seasonal.groupby(["region", "account_id", "expected_monthly_turnover_inr"], as_index=False)["amount_inr"].sum()
    seasonal_totals["turnover_ratio"] = seasonal_totals["amount_inr"] / seasonal_totals["expected_monthly_turnover_inr"]
    candidates = seasonal_totals.loc[seasonal_totals["amount_inr"].gt(5_000_000) & seasonal_totals["turnover_ratio"].le(0.75)]
    if not candidates.empty:
        candidate = candidates.sort_values("amount_inr", ascending=False).iloc[0]
        rows.append(
            {
                "finding_id": "ALT-SEASONAL-001",
                "finding_type": "Alternative hypothesis",
                "region": candidate["region"],
                "title": "Seasonal cash increase remains within documented profile",
                "decision": "MONITOR",
                "confidence": 0.84,
                "pattern_strength": 0.48,
                "method": "Expected-turnover and relationship check",
                "summary": f"Recent activity is {candidate['turnover_ratio']:.0%} of documented monthly turnover and has no material relationship cluster.",
                "supporting_evidence": "KYC is fresh and the business is documented as cash-intensive.",
                "contradicting_evidence": "Activity is elevated and should remain observable during the seasonal window.",
                "alternative_hypothesis": "Seasonal business activity is directly supported by the current profile.",
                "requested_information": "Monitor for seven days and compare with the documented seasonal profile.",
                "account_ids": [candidate["account_id"]],
                "cluster_id": "",
            }
        )

    # S4: Sparse history channel -> PEER_BASED
    for channel, group in data.enriched.groupby("channel"):
        history_days = int((group["timestamp"].max().floor("D") - group["timestamp"].min().floor("D")).days + 1)
        if history_days >= 28 or len(group) < 20:
            continue
        region = str(group["region"].mode().iloc[0])
        peers = data.enriched.loc[data.enriched["channel"].ne(channel) & data.enriched["region"].eq(region)]
        peer_sufficient = peers["branch_id"].nunique() >= 3
        rows.append(
            {
                "finding_id": f"SPARSE-{channel}",
                "finding_type": "Sparse history",
                "region": region,
                "title": f"{channel} uses a peer-based baseline",
                "decision": "PEER_BASED" if peer_sufficient else "ABSTAIN",
                "confidence": 0.64 if peer_sufficient else 0.48,
                "pattern_strength": 0.42,
                "method": f"Peer channels and branches; confidence capped ({history_days} days of history)",
                "summary": f"{channel} has {history_days} days of history, below the 28-day governed minimum.",
                "supporting_evidence": f"{len(group):,} events are compared with {peers['branch_id'].nunique()} peer branches.",
                "contradicting_evidence": "A stable long-history baseline is unavailable.",
                "alternative_hypothesis": "Launch effects may explain the movement.",
                "requested_information": "Continue collecting history and review peer comparability.",
                "account_ids": sorted(group["account_id"].unique().tolist()),
                "cluster_id": "",
            }
        )

    findings = pd.DataFrame(rows)
    if findings.empty:
        return pd.DataFrame(columns=["finding_id", "finding_type", "region", "title", "decision", "confidence", "pattern_strength", "method", "summary", "supporting_evidence", "contradicting_evidence", "alternative_hypothesis", "requested_information", "account_ids", "cluster_id"])
    order = pd.Categorical(findings["decision"], ["ALERT", "ABSTAIN", "PEER_BASED", "MONITOR"], ordered=True)
    return findings.assign(_order=order).sort_values(["_order", "confidence"], ascending=[True, False]).drop(columns="_order").reset_index(drop=True)
