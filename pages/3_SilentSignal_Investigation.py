"""Connected-pattern, evidence, confidence, and abstention workspace."""

from __future__ import annotations

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.evidence import build_evidence_packet, llm_payload
from src.narrative import narrative_from_packet
from src.security import mask_identifier
from src.ui import (
    configure_page,
    decision_chip,
    get_demo_runtime,
    render_decision_banner,
    render_page_header,
    render_project_banner,
    render_section_header,
    render_sidebar,
)


configure_page("SilentSignal Investigation", "🔗")
bundle, user, region = render_sidebar()
runtime = get_demo_runtime()

render_page_header(
    "Pattern investigation",
    "SilentSignal investigation",
    "Review connected activity, evidence quality, alternative hypotheses, and explicit uncertainty as separate concepts.",
    f"Authorised · {region}",
)
render_project_banner()

findings = runtime.analysis.findings.loc[runtime.analysis.findings["region"].eq(region)]
if findings.empty:
    st.success("No active findings for this region.")
    st.stop()

render_section_header(
    "Select an investigation focus",
    "Only findings inside the current persona and regional entitlement are available.",
    "Case context",
)
finding_id = st.selectbox(
    "Finding",
    options=findings["finding_id"].tolist(),
    format_func=lambda value: findings.set_index("finding_id").loc[value, "title"],
)
finding = findings.loc[findings["finding_id"].eq(finding_id)].iloc[0]
packet = build_evidence_packet(runtime.data, runtime.analysis, bundle, user, region, finding_id)

left, right = st.columns([4, 1])
with left:
    st.markdown(f"## {finding['title']}")
    st.markdown(decision_chip(finding["decision"]), unsafe_allow_html=True)
    st.caption(f"{finding['finding_type']} · {finding['method']}")
with right:
    st.metric("Evidence confidence", f"{finding['confidence']:.0%}")
    st.metric("Pattern strength", f"{finding['pattern_strength']:.0%}")

if finding["decision"] == "ABSTAIN":
    render_decision_banner(
        "ABSTAIN",
        "Evidence gate active",
        f"High-impact escalation is blocked. {finding['requested_information']}",
    )
elif finding["decision"] == "ALERT":
    render_decision_banner(
        "ALERT",
        "Priority human review",
        "The connected risk signal is material; it is not a conclusion of wrongdoing.",
    )
else:
    render_decision_banner(
        str(finding["decision"]),
        "Governed monitoring path",
        "Current evidence does not support a high-impact action.",
    )

render_section_header(
    "Persona-specific briefing",
    "Language is rendered from the validated evidence packet after access and redaction checks.",
    "Decision narrative",
)
st.write(narrative_from_packet(packet))

tab_graph, tab_evidence, tab_transactions, tab_trace = st.tabs(["Relationship view", "Evidence packet", "Activity", "Execution trace"])

with tab_graph:
    accounts = list(finding["account_ids"])
    if finding["cluster_id"] and len(accounts) > 1:
        graph = runtime.analysis.relationships.graph.subgraph(accounts).copy()
        positions = nx.spring_layout(graph, seed=42)
        edge_x: list[float | None] = []
        edge_y: list[float | None] = []
        for left_node, right_node in graph.edges():
            x0, y0 = positions[left_node]
            x1, y1 = positions[right_node]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        edge_trace = go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1.5, color="#b8bdd0"), hoverinfo="none")
        node_x, node_y, labels, hover = [], [], [], []
        for index, account in enumerate(graph.nodes()):
            x, y = positions[account]
            node_x.append(x)
            node_y.append(y)
            labels.append(mask_identifier(account) if user.can_view_entity_detail else f"Account {index + 1}")
            types = sorted({kind for neighbor in graph.neighbors(account) for kind in graph[account][neighbor]["types"]})
            hover.append(" · ".join(types) or "Relationship evidence")
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            hovertext=hover,
            hoverinfo="text",
            marker=dict(size=24, color="#6652e8", line=dict(width=3, color="#e9e6ff")),
        )
        figure = go.Figure([edge_trace, node_trace])
        figure.update_layout(
            template="plotly_white",
            height=490,
            margin=dict(l=20, r=20, t=25, b=20),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hoverlabel=dict(bgcolor="#102036", font_color="white", bordercolor="#102036"),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
        st.caption("Nodes are masked synthetic accounts. Edges represent shared governed identifiers or beneficiaries; no graph-neural model is used.")
    else:
        st.info("This finding is evidence-based but does not assert a connected entity cluster.")

with tab_evidence:
    for evidence in packet["evidence"]:
        st.markdown(
            f"<div class='ss-evidence'><strong>{evidence['evidence_id']} · {evidence['kind']}</strong><br>{evidence['statement']}</div><br>",
            unsafe_allow_html=True,
        )
    c1, c2 = st.columns(2)
    c1.metric("Fresh source feeds", f"{runtime.data.source_freshness['status'].eq('Fresh').mean():.0%}")
    c2.metric("Confidence gate", "Pass" if finding["confidence"] >= bundle.settings.analysis.abstention_confidence_below else "Abstain")
    with st.expander("Complete structured evidence packet"):
        st.json(llm_payload(packet), expanded=False)

with tab_transactions:
    activity = runtime.data.enriched.loc[
        runtime.data.enriched["account_id"].isin(finding["account_ids"])
        & runtime.data.enriched["timestamp"].ge(runtime.data.as_of - pd.Timedelta(days=14))
    ].copy()
    if activity.empty:
        st.caption("No transaction-level evidence applies to this finding.")
    elif user.can_view_entity_detail:
        activity["account"] = activity["account_id"].map(mask_identifier)
        table = activity[["timestamp", "account", "amount_inr", "branch_id", "channel", "is_near_threshold", "kyc_fresh"]].sort_values("timestamp", ascending=False)
        st.dataframe(table, width="stretch", hide_index=True, column_config={"amount_inr": st.column_config.NumberColumn("Amount", format="₹%,.0f")})
    else:
        aggregate = activity.groupby(["branch_id", "channel"], as_index=False).agg(transactions=("transaction_id", "nunique"), value_inr=("amount_inr", "sum"), accounts=("account_id", "nunique"))
        st.dataframe(aggregate, width="stretch", hide_index=True, column_config={"value_inr": st.column_config.NumberColumn("Value", format="₹%,.0f")})
        st.caption("Entity detail is suppressed for the Compliance Head persona.")

with tab_trace:
    st.code(
        """1. Enforce persona + region entitlement
2. Reconcile transaction IDs to KYC and source metadata
3. Calculate governed KPI values in Python
4. Build transparent NetworkX relationships
5. Score pattern strength separately from evidence confidence
6. Apply critical quality and abstention gates
7. Render deterministic evidence-linked narrative
8. Offer only role-permitted playbook actions""",
        language="text",
    )
    st.caption("LLM calls: 0 · Raw identifiers sent to an LLM: 0 · Ground-truth records used by analysis: 0 · Narrative inputs: evidence packet only")
