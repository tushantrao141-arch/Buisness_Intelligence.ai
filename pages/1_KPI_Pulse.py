"""Prioritised governed KPI movement page."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.ui import configure_page, format_kpi_value, get_demo_runtime, render_project_banner, render_sidebar


configure_page("KPI Pulse", "📊")
bundle, user, region = render_sidebar()
runtime = get_demo_runtime()

st.markdown('<div class="ss-eyebrow">GOVERNED MONITORING</div>', unsafe_allow_html=True)
st.title("KPI Pulse")
st.write("Prioritised movements combine a governed baseline, business materiality, and evidence readiness.")
render_project_banner()

kpi_by_id = {kpi.id: kpi for kpi in bundle.kpis}
scope = runtime.analysis.movements.loc[runtime.analysis.movements["region"].eq(region)].copy()
scope["name"] = scope["kpi_id"].map(lambda value: kpi_by_id[value].name)

metric_columns = st.columns(5)
for column, movement in zip(metric_columns, scope.sort_values("name").itertuples(index=False)):
    column.metric(
        movement.name,
        format_kpi_value(movement.kpi_id, movement.actual),
        f"{movement.delta:+,.1f} vs expected",
        help=kpi_by_id[movement.kpi_id].description,
        delta_color="inverse" if movement.kpi_id == "case_sla_risk" else "normal",
    )

selected_kpi = st.selectbox(
    "Trend to inspect",
    options=list(kpi_by_id),
    format_func=lambda kpi_id: kpi_by_id[kpi_id].name,
)
history = runtime.analysis.history.loc[
    runtime.analysis.history["region"].eq(region) & runtime.analysis.history["kpi_id"].eq(selected_kpi)
]
movement = scope.loc[scope["kpi_id"].eq(selected_kpi)].iloc[0]

left, right = st.columns([4, 1])
with left:
    figure = px.line(history, x="date", y="value", markers=False, template="plotly_white")
    figure.add_hline(y=movement.expected, line_dash="dash", line_color="#df7a54", annotation_text="28-day baseline")
    figure.update_traces(line_color="#6652e8", line_width=3, fill="tozeroy", fillcolor="rgba(102,82,232,.08)")
    figure.update_layout(height=350, margin=dict(l=10, r=10, t=15, b=10), yaxis_title=kpi_by_id[selected_kpi].unit, xaxis_title=None)
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
with right:
    st.metric("Impact score", f"{movement.impact_score:.0f}/100")
    st.metric("Standard score", f"{movement.z_score:+.1f}σ")
    st.metric("Material", "Yes" if movement.material else "No")
    st.caption(movement.baseline_method)

st.markdown("### Movement queue")
queue = scope[["name", "actual", "expected", "delta_pct", "z_score", "impact_score", "material"]].copy()
queue.columns = ["KPI", "Actual", "Expected", "Δ %", "Z-score", "Impact", "Material"]
st.dataframe(
    queue,
    width="stretch",
    hide_index=True,
    column_config={
        "Actual": st.column_config.NumberColumn(format="%.2f"),
        "Expected": st.column_config.NumberColumn(format="%.2f"),
        "Δ %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Z-score": st.column_config.NumberColumn(format="%+.2f"),
        "Impact": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f"),
    },
)

with st.expander("KPI semantic contract and lineage"):
    contract = kpi_by_id[selected_kpi]
    a, b, c = st.columns(3)
    a.markdown(f"**Owner**  \n{contract.owner}")
    b.markdown(f"**Grain**  \n{contract.grain.replace('_', ' ')}")
    c.markdown(f"**Refresh SLA**  \n{contract.refresh_sla_hours:g} hours")
    st.markdown(f"**Definition**  \n{contract.description}")
    st.markdown(f"**Sources**  \n{', '.join(contract.sources)}")
    st.markdown(f"**Governed drivers**  \n{', '.join(contract.drivers)}")

