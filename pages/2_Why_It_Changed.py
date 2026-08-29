"""Driver contribution and alternative-hypothesis page."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.ui import configure_page, format_kpi_value, get_demo_runtime, render_project_banner, render_sidebar


configure_page("Why It Changed", "🧭")
bundle, user, region = render_sidebar()
runtime = get_demo_runtime()
kpi_by_id = {kpi.id: kpi for kpi in bundle.kpis}

st.markdown('<div class="ss-eyebrow">EXPLANATION</div>', unsafe_allow_html=True)
st.title("Why it changed")
st.write("Observed movement is decomposed into traceable segment contributions. Alternative explanations remain visible.")
render_project_banner()

available = ["near_threshold_value_ratio", "linked_pattern_exposure", "high_risk_cluster_count"]
selected_kpi = st.selectbox("KPI", available, format_func=lambda kpi_id: kpi_by_id[kpi_id].name)
movement = runtime.analysis.movements.loc[
    runtime.analysis.movements["region"].eq(region) & runtime.analysis.movements["kpi_id"].eq(selected_kpi)
].iloc[0]

a, b, c, d = st.columns(4)
a.metric("Observed", format_kpi_value(selected_kpi, movement.actual))
b.metric("Expected", format_kpi_value(selected_kpi, movement.expected))
c.metric("Movement", f"{movement.delta_pct:+.1f}%")
d.metric("Impact", f"{movement.impact_score:.0f}/100")

drivers = runtime.analysis.drivers.loc[
    runtime.analysis.drivers["region"].eq(region) & runtime.analysis.drivers["kpi_id"].eq(selected_kpi)
].copy()
if drivers.empty:
    st.info("No material driver contribution is available for this scope.")
else:
    ranked = drivers.reindex(drivers["contribution"].abs().sort_values(ascending=False).index)
    top = ranked.head(8)
    other = float(ranked.iloc[8:]["contribution"].sum())
    labels = ["Expected", *[text[:30] + ("…" if len(text) > 30 else "") for text in top["driver"]]]
    values = [float(movement.expected), *top["contribution"].astype(float).tolist()]
    measures = ["absolute", *(["relative"] * len(top))]
    if abs(other) > 1e-9:
        labels.append("Other reconciled leaves")
        values.append(other)
        measures.append("relative")
    labels.append("Observed")
    values.append(float(movement.actual))
    measures.append("total")
    figure = go.Figure(
        go.Waterfall(
            x=labels,
            y=values,
            measure=measures,
            connector={"line": {"color": "#9da3b5"}},
            increasing={"marker": {"color": "#6652e8"}},
            decreasing={"marker": {"color": "#df7a54"}},
            totals={"marker": {"color": "#17213a"}},
        )
    )
    figure.update_layout(template="plotly_white", height=480, margin=dict(l=10, r=10, t=20, b=80), yaxis_title=f"Contribution ({kpi_by_id[selected_kpi].unit})", xaxis_title=None)
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})

    detail = ranked.head(15)[["driver", "actual", "expected", "contribution", "contribution_pct", "unexplained"]]
    value_format = "₹%,.0f" if selected_kpi == "linked_pattern_exposure" else "%.4f"
    st.dataframe(
        detail,
        width="stretch",
        hide_index=True,
        column_config={
            "driver": "Driver",
            "actual": st.column_config.NumberColumn("Observed value", format=value_format),
            "expected": st.column_config.NumberColumn("Expected value", format=value_format),
            "contribution": st.column_config.NumberColumn("Contribution", format=value_format),
            "contribution_pct": st.column_config.NumberColumn("Contribution %", format="%+.1f%%"),
            "unexplained": st.column_config.NumberColumn("Unexplained", format="%.6f"),
        },
    )
    st.success(f"Reconciliation passed: explained {drivers['explained_total'].iloc[0]:,.4f} of {drivers['movement_total'].iloc[0]:,.4f}; unexplained {drivers['unexplained'].iloc[0]:.8f}.")

st.markdown("### Supported alternatives and limits")
alternatives = runtime.analysis.findings.loc[
    runtime.analysis.findings["region"].eq(region)
    & runtime.analysis.findings["finding_type"].isin(["Alternative hypothesis", "Evidence gap", "Sparse history"])
]
if alternatives.empty:
    st.caption("No distinct alternative-hypothesis finding is active for this region.")
for finding in alternatives.itertuples(index=False):
    with st.container(border=True):
        st.markdown(f"**{finding.title}**")
        st.write(finding.alternative_hypothesis)
        st.caption(f"Contradicting evidence: {finding.contradicting_evidence}")

with st.expander("Method and reproducibility"):
    st.write("Each transaction is assigned to one mutually exclusive leaf across region, branch, channel, account age, customer category, and qualifying cluster. Current seven-day leaf contributions are compared with the prior 28-day baseline and sum exactly to the KPI movement. No language model performs arithmetic.")
    st.code(f"scope={region} · kpi={selected_kpi} · baseline=28d · window=7d", language="text")
