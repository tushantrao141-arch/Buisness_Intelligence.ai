"""SilentSignal executive landing page."""

from __future__ import annotations

import streamlit as st

from src.evaluation import evaluation_summary
from src.ui import configure_page, decision_chip, format_kpi_value, get_demo_runtime, render_project_banner, render_sidebar


configure_page("Command Center", "🛡️")
bundle, user, region = render_sidebar()
runtime = get_demo_runtime()

st.markdown(
    """
    <div class="ss-hero">
      <div class="ss-eyebrow" style="color:#bdb5ff">BUSINESSINTELLIGENCE.AI</div>
      <h2>See the movement. Trace the signal. Take the permitted action.</h2>
      <p>SilentSignal reconciles fragmented risk data, detects material KPI movement,
      connects related activity, and makes uncertainty visible before a human decision.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
render_project_banner()

scope = runtime.analysis.movements.loc[runtime.analysis.movements["region"].eq(region)]
material = int(scope["material"].sum())
alerts = runtime.analysis.findings.loc[
    runtime.analysis.findings["region"].eq(region) & runtime.analysis.findings["decision"].eq("ALERT")
]
abstentions = runtime.analysis.findings.loc[
    runtime.analysis.findings["region"].eq(region) & runtime.analysis.findings["decision"].eq("ABSTAIN")
]
evaluation = evaluation_summary(runtime.evaluation)

columns = st.columns(4)
columns[0].metric("Material KPI movements", material, help="Five governed KPI contracts are evaluated.")
columns[1].metric("Priority patterns", len(alerts), help="Review signals, not conclusions of wrongdoing.")
columns[2].metric("Evidence abstentions", len(abstentions), help="High-impact recommendations are blocked when evidence is insufficient.")
columns[3].metric("Acceptance scenarios", f"{evaluation['passed']}/{evaluation['scenario_count']}", help="Calculated from held-out synthetic ground truth.")

st.markdown("### What needs attention")
region_findings = runtime.analysis.findings.loc[runtime.analysis.findings["region"].eq(region)]
if region_findings.empty:
    st.success("No priority findings in the selected region.")
else:
    for finding in region_findings.head(4).itertuples(index=False):
        with st.container(border=True):
            left, right = st.columns([5, 1])
            left.markdown(f"#### {finding.title}")
            left.markdown(decision_chip(finding.decision), unsafe_allow_html=True)
            left.caption(f"{finding.finding_type} · {finding.method}")
            right.metric("Confidence", f"{finding.confidence:.0%}")
            st.write(finding.summary)

st.markdown("### Governed KPI snapshot")
kpi_names = {kpi.id: kpi.name for kpi in bundle.kpis}
kpi_columns = st.columns(5)
for column, movement in zip(kpi_columns, scope.sort_values("kpi_id").itertuples(index=False)):
    column.metric(
        kpi_names[movement.kpi_id],
        format_kpi_value(movement.kpi_id, movement.actual),
        f"{movement.delta_pct:+.1f}% vs baseline",
        delta_color="inverse" if movement.kpi_id == "case_sla_risk" else "normal",
    )

left, right = st.columns([3, 2])
with left:
    st.markdown("### Intelligence-to-action controls")
    stages = [
        ("01", "Reconcile", "Three sources, different grains and cadences"),
        ("02", "Calculate", "Five deterministic governed KPIs"),
        ("03", "Connect", "Transparent entity and beneficiary graph"),
        ("04", "Explain", "Ranked drivers, evidence, alternatives, confidence"),
        ("05", "Act", "Role-limited playbook with feedback and audit"),
    ]
    for number, name, detail in stages:
        st.markdown(f"**{number} · {name}**  \n<span class='ss-muted'>{detail}</span>", unsafe_allow_html=True)
with right:
    st.markdown("### Source health")
    for source in runtime.data.source_freshness.itertuples(index=False):
        icon = "●" if source.status == "Fresh" else "▲"
        st.markdown(f"**{icon} {source.source.title()}** · {source.status}  \n{source.row_count:,} rows · {source.age_hours:.1f}h old")
    st.caption(f"Full analysis completed in {runtime.latency_ms:,.0f} ms · 0 model calls · ₹0 model cost")

st.warning("A review score is not proof of illegal conduct. High-impact decisions remain with authorised human users.")

