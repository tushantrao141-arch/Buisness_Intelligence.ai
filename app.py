"""SilentSignal executive landing page."""

from __future__ import annotations

from html import escape

import streamlit as st

from src.evaluation import evaluation_summary
from src.ui import (
    configure_page,
    format_kpi_value,
    get_demo_runtime,
    render_finding_card,
    render_project_banner,
    render_section_header,
    render_sidebar,
)


configure_page("Command Center", "🛡️")
bundle, user, region = render_sidebar()
runtime = get_demo_runtime()

scope = runtime.analysis.movements.loc[runtime.analysis.movements["region"].eq(region)]
material = int(scope["material"].sum())
region_findings = runtime.analysis.findings.loc[runtime.analysis.findings["region"].eq(region)]
alerts = region_findings.loc[region_findings["decision"].eq("ALERT")]
abstentions = region_findings.loc[region_findings["decision"].eq("ABSTAIN")]
evaluation = evaluation_summary(runtime.evaluation)

st.markdown(
    f"""
    <div class="ss-hero">
      <div>
        <div class="ss-eyebrow">BUSINESSINTELLIGENCE.AI · DECISION WORKSPACE</div>
        <h1>Risk intelligence that ends in a defensible action.</h1>
        <p>SilentSignal turns governed KPI movement into connected evidence, explicit uncertainty,
        and the next action this user is permitted to take.</p>
        <div class="ss-hero-pills">
          <span class="ss-hero-pill">{escape(region)} scope</span>
          <span class="ss-hero-pill">{escape(user.display_name)}</span>
          <span class="ss-hero-pill">Human decision required</span>
          <span class="ss-hero-pill">No autonomous action</span>
        </div>
      </div>
      <div class="ss-hero-panel">
        <div class="ss-panel-label">Priority review signals</div>
        <div class="ss-panel-value">{len(alerts):02d}</div>
        <div class="ss-panel-note">Signals requiring authorised human attention</div>
        <div class="ss-signal-row"><span>Material KPI movements</span><strong>{material} / 5</strong></div>
        <div class="ss-signal-row"><span>Evidence-gated abstentions</span><strong>{len(abstentions):02d}</strong></div>
        <div class="ss-signal-row"><span>Acceptance scenarios</span><strong>{evaluation['passed']} / {evaluation['scenario_count']}</strong></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
render_project_banner()

columns = st.columns(4)
columns[0].metric("Material movements", material, help="Five governed KPI contracts are evaluated.")
columns[1].metric("Priority patterns", len(alerts), help="Review signals, not conclusions of wrongdoing.")
columns[2].metric("Evidence abstentions", len(abstentions), help="High-impact recommendations are blocked when evidence is insufficient.")
columns[3].metric("Scenario assurance", f"{evaluation['acceptance_rate']:.0%}", help="Calculated from held-out synthetic ground truth.")

render_section_header(
    "What needs attention",
    "Ranked by decision state and evidence confidence for the selected region.",
    "Priority work queue",
)
if region_findings.empty:
    st.success("No priority findings in the selected region.")
else:
    decision_order = {"ALERT": 0, "ABSTAIN": 1, "PEER_BASED": 2, "MONITOR": 3}
    ordered = region_findings.assign(
        decision_rank=region_findings["decision"].map(decision_order).fillna(9)
    ).sort_values(["decision_rank", "confidence"], ascending=[True, False])
    for finding in ordered.head(4).itertuples(index=False):
        render_finding_card(finding)

render_section_header(
    "Governed KPI snapshot",
    "Actual values and movement are calculated from the selected regional slice.",
    "Portfolio pulse",
)
kpi_names = {kpi.id: kpi.name for kpi in bundle.kpis}
kpi_columns = st.columns(5)
for column, movement in zip(kpi_columns, scope.sort_values("kpi_id").itertuples(index=False)):
    column.metric(
        kpi_names[movement.kpi_id],
        format_kpi_value(movement.kpi_id, movement.actual),
        f"{movement.delta_pct:+.1f}% vs baseline",
        delta_color="inverse" if movement.kpi_id == "case_sla_risk" else "normal",
    )

render_section_header(
    "From fragmented data to governed action",
    "Every step stays deterministic, inspectable, and role-aware.",
    "Operating model",
)
st.markdown(
    """
    <div class="ss-flow">
      <div class="ss-flow-step"><div class="ss-flow-number">01 · INPUT</div><div class="ss-flow-title">Reconcile</div><div class="ss-flow-detail">Transactions, KYC, and cases aligned across grain and cadence.</div></div>
      <div class="ss-flow-step"><div class="ss-flow-number">02 · MEASURE</div><div class="ss-flow-title">Calculate</div><div class="ss-flow-detail">Five deterministic KPIs compared with governed baselines.</div></div>
      <div class="ss-flow-step"><div class="ss-flow-number">03 · CONNECT</div><div class="ss-flow-title">Detect patterns</div><div class="ss-flow-detail">Transparent account, beneficiary, branch, and identifier links.</div></div>
      <div class="ss-flow-step"><div class="ss-flow-number">04 · EXPLAIN</div><div class="ss-flow-title">Build evidence</div><div class="ss-flow-detail">Drivers, alternatives, freshness, and confidence kept separate.</div></div>
      <div class="ss-flow-step"><div class="ss-flow-number">05 · RESPOND</div><div class="ss-flow-title">Take action</div><div class="ss-flow-detail">Persona-permitted playbook steps with feedback and audit.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_section_header(
    "Source readiness",
    f"Full analysis completed in {runtime.latency_ms:,.0f} ms with zero model calls and ₹0 model cost.",
    "Operational health",
)
health_cards = []
for source in runtime.data.source_freshness.itertuples(index=False):
    source_name = {"transactions": "Transactions", "kyc": "KYC", "cases": "Cases"}.get(
        source.source,
        source.source.title(),
    )
    health_cards.append(
        f'<div class="ss-health-card"><div class="ss-health-top">'
        f'<span class="ss-health-name">{escape(source_name)}</span>'
        f'<span class="ss-health-state">● {escape(source.status)}</span></div>'
        f'<div class="ss-health-meta">{source.row_count:,} rows · {source.age_hours:.1f} hours old · '
        f'{source.sla_hours:g}h SLA</div></div>'
    )
st.markdown(f'<div class="ss-health-grid">{"".join(health_cards)}</div>', unsafe_allow_html=True)

st.warning(
    "A review score is a prioritisation signal—not proof of illegal conduct. "
    "High-impact decisions remain with authorised human users."
)
