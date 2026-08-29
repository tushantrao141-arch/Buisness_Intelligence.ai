"""Governed action workspace with a durable local audit trail."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.narrative import recommended_action_ids
from src.storage import read_events, record_action
from src.ui import configure_page, decision_chip, get_demo_runtime, render_project_banner, render_sidebar


PROJECT_ROOT = Path(__file__).resolve().parents[1]
configure_page("Actions", "✅")
bundle, user, region = render_sidebar()
runtime = get_demo_runtime()

st.markdown('<div class="ss-eyebrow">GOVERNED RESPONSE</div>', unsafe_allow_html=True)
st.title("Action workspace")
st.write("Recommendations are selected from the configured playbook after evidence and access gates have passed.")
render_project_banner()

findings = runtime.analysis.findings.loc[runtime.analysis.findings["region"].eq(region)]
if findings.empty:
    st.success("There are no findings requiring action in this region.")
    st.stop()

finding_id = st.selectbox("Finding", findings["finding_id"].tolist(), format_func=lambda value: findings.set_index("finding_id").loc[value, "title"])
finding = findings.loc[findings["finding_id"].eq(finding_id)].iloc[0]
st.markdown(decision_chip(finding["decision"]), unsafe_allow_html=True)
st.write(finding["summary"])

action_ids = recommended_action_ids(finding, user, bundle)
actions = {action.id: action for action in bundle.actions}

st.markdown("### Permitted recommendations")
if not action_ids:
    st.info("No configured action is both evidence-supported and permitted for this persona. Continue monitoring or request authorised review.")
for action_id in action_ids:
    action = actions[action_id]
    expected_reduction = round(5 + 12 * float(finding["confidence"]) * float(finding["pattern_strength"]), 1)
    with st.container(border=True):
        left, right = st.columns([4, 1])
        left.markdown(f"#### {action.action}")
        left.caption(f"Owner · {action.owner}  |  Lever · {action.lever.replace('_', ' ')}")
        left.write(f"Monitor **{actions[action_id].monitoring_kpi.replace('_', ' ')}** using **{action.expected_impact_method.replace('_', ' ')}**.")
        right.metric("Simulated impact", f"{expected_reduction:.1f}%", help="Calculated demonstration estimate, not a production forecast.")
        approve, reject = st.columns(2)
        payload = {"region": region, "confidence": float(finding["confidence"]), "expected_reduction_pct": expected_reduction}
        if approve.button("Approve and record", key=f"approve_{finding_id}_{action_id}", type="primary"):
            record_action(PROJECT_ROOT, user.id, finding_id, action_id, status="ACCEPTED", payload=payload)
            st.success("Accepted action recorded in the local audit trail.")
        if reject.button("Reject and record", key=f"reject_{finding_id}_{action_id}"):
            record_action(PROJECT_ROOT, user.id, finding_id, action_id, status="REJECTED", payload=payload)
            st.info("Rejected action recorded for governance review.")

if finding["decision"] == "ABSTAIN":
    st.warning("Abstention blocks escalation, consolidation, filing, or account restriction. Only information-gathering actions are offered.")

st.markdown("### Recent action trail")
history = read_events(PROJECT_ROOT, "action_events", limit=20)
history = history.loc[history["user_id"].eq(user.id)] if not history.empty else history
if history.empty:
    st.caption("No actions have been recorded for this persona yet.")
else:
    st.dataframe(history[["created_at", "finding_id", "action_id", "status"]], width="stretch", hide_index=True)
