"""Relationship graph, connected components, and cluster risk scoring."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd

from src.data import DataBundle


@dataclass(frozen=True)
class RelationshipResult:
    """Account graphs, scored clusters, and transaction-to-cluster membership."""

    graph: nx.Graph
    heterogeneous_graph: nx.Graph
    clusters: pd.DataFrame
    transaction_clusters: pd.DataFrame


def build_relationships(data: DataBundle, weights: dict | None = None) -> RelationshipResult:
    """Connect accounts through governed shared identifiers and beneficiaries."""
    graph = nx.Graph()
    for row in data.kyc.itertuples(index=False):
        graph.add_node(row.account_id, region=None, risk_tier=row.risk_tier)

    def connect_groups(frame: pd.DataFrame, value_column: str, relationship: str) -> None:
        clean = frame.loc[frame[value_column].fillna("").astype(str).str.len().gt(0)]
        for value, group in clean.groupby(value_column):
            accounts = sorted(set(group["account_id"].astype(str)))
            if 2 <= len(accounts) <= 10:
                for left, right in combinations(accounts, 2):
                    if graph.has_edge(left, right):
                        graph[left][right]["types"].add(relationship)
                    else:
                        graph.add_edge(left, right, types={relationship}, shared_value=str(value))

    connect_groups(data.kyc, "phone_hash", "shared phone")
    connect_groups(data.kyc, "address_hash", "shared address")
    connect_groups(data.transactions, "beneficiary_hash", "shared beneficiary")

    cluster_rows: list[dict] = []
    membership_rows: list[dict] = []
    cluster_number = 1
    tx = data.enriched

    base_score = 18
    account_weight = 7
    near_weight = 2
    branch_weight = 4
    edge_weight = 7

    for component in nx.connected_components(graph):
        if len(component) < 2:
            continue
        component_tx = tx.loc[tx["account_id"].isin(component)]
        if component_tx.empty:
            continue
        region = str(component_tx["region"].mode().iloc[0])
        edge_types = set()
        for _, _, edge in graph.subgraph(component).edges(data=True):
            edge_types.update(edge["types"])
        recent = component_tx.loc[component_tx["timestamp"].ge(data.as_of - pd.Timedelta(days=14))]
        near_count = int(recent["is_near_threshold"].sum())
        branch_count = int(recent["branch_id"].nunique())
        risk_score = min(
            100,
            base_score + (len(component) - 1) * account_weight + min(near_count, 16) * near_weight + max(0, branch_count - 1) * branch_weight + len(edge_types) * edge_weight,
        )
        cluster_id = f"SS-{region[:1]}-{cluster_number:03d}"
        qualifies = risk_score >= 60 and near_count >= 4
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "region": region,
                "account_count": len(component),
                "transaction_count": len(recent),
                "near_threshold_count": near_count,
                "branch_count": branch_count,
                "relationship_types": ", ".join(sorted(edge_types)),
                "exposure_inr": float(recent["amount_inr"].sum()),
                "risk_score": int(risk_score),
                "qualifies": bool(qualifies),
                "account_ids": sorted(component),
            }
        )
        for transaction_id in component_tx["transaction_id"]:
            membership_rows.append(
                {
                    "transaction_id": transaction_id,
                    "cluster_id": cluster_id,
                    "qualifies": bool(qualifies),
                    "risk_score": int(risk_score),
                }
            )
        for account_id in component:
            graph.nodes[account_id]["cluster_id"] = cluster_id
            graph.nodes[account_id]["region"] = region
        cluster_number += 1

    clusters = pd.DataFrame(cluster_rows)
    memberships = pd.DataFrame(membership_rows)
    if clusters.empty:
        clusters = pd.DataFrame(columns=["cluster_id", "region", "account_count", "transaction_count", "near_threshold_count", "branch_count", "relationship_types", "exposure_inr", "risk_score", "qualifies", "account_ids"])
    if memberships.empty:
        memberships = pd.DataFrame(columns=["transaction_id", "cluster_id", "qualifies", "risk_score"])

    heterogeneous = nx.Graph()
    for row in data.kyc.itertuples(index=False):
        customer_node = f"customer:{row.customer_id}"
        account_node = f"account:{row.account_id}"
        heterogeneous.add_node(customer_node, entity_type="customer", label="Masked customer")
        heterogeneous.add_node(account_node, entity_type="account", label=row.account_id)
        heterogeneous.add_edge(customer_node, account_node, relationship="owns")
        for relationship, value in (("phone", row.phone_hash), ("address", row.address_hash)):
            if pd.notna(value) and str(value):
                identifier_node = f"{relationship}:{value}"
                heterogeneous.add_node(identifier_node, entity_type="shared_identifier", label=f"Shared {relationship}")
                heterogeneous.add_edge(account_node, identifier_node, relationship=f"has {relationship}")

    recent_tx = data.transactions.loc[data.transactions["timestamp"].ge(data.as_of - pd.Timedelta(days=14))]
    for row in recent_tx.itertuples(index=False):
        account_node = f"account:{row.account_id}"
        transaction_node = f"transaction:{row.transaction_id}"
        branch_node = f"branch:{row.branch_id}"
        heterogeneous.add_node(transaction_node, entity_type="transaction", label="Transaction evidence")
        heterogeneous.add_node(branch_node, entity_type="branch", label=row.branch_id)
        heterogeneous.add_edge(account_node, transaction_node, relationship="initiated")
        heterogeneous.add_edge(transaction_node, branch_node, relationship="originated at")
        if pd.notna(row.beneficiary_hash) and str(row.beneficiary_hash):
            beneficiary_node = f"beneficiary:{row.beneficiary_hash}"
            heterogeneous.add_node(beneficiary_node, entity_type="beneficiary", label="Masked beneficiary")
            heterogeneous.add_edge(transaction_node, beneficiary_node, relationship="benefits")

    return RelationshipResult(graph, heterogeneous, clusters, memberships)
