"""Data quality, evaluation, security, feedback, and runtime governance."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import streamlit as st

from src.config import get_user
from src.evaluation import evaluation_summary
from src.security import check_access
from src.storage import read_events, record_feedback, record_security
from src.ui import (
    configure_page,
    get_demo_runtime,
    render_decision_banner,
    render_page_header,
    render_project_banner,
    render_section_header,
    render_sidebar,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
configure_page("Governance", "⚙️")
bundle, user, region = render_sidebar()
runtime = get_demo_runtime()
summary = evaluation_summary(runtime.evaluation)

render_page_header(
    "Control plane",
    "Governance and evaluation",
    "Calculated controls make freshness, quality, security, abstention, evaluation, and runtime behaviour inspectable.",
    "Audit-ready",
)
render_project_banner()

render_section_header(
    "Control posture",
    "A compact view of source readiness, scenario assurance, and model usage.",
    "Live assurance",
)
columns = st.columns(4)
columns[0].metric("Source freshness", f"{runtime.data.source_freshness['status'].eq('Fresh').mean():.0%}")
columns[1].metric("Critical DQ failures", int(runtime.data.quality.loc[runtime.data.quality["severity"].eq("critical"), "affected_rows"].sum()))
columns[2].metric("Acceptance rate", f"{summary['acceptance_rate']:.0%}")
columns[3].metric("Model calls / cost", "0 / US$0.00")

tab_quality, tab_eval, tab_benchmark, tab_security, tab_runtime, tab_feedback = st.tabs(["Data quality", "Held-out evaluation", "Method comparison", "Security", "Runtime", "Feedback"])

with tab_quality:
    st.markdown("#### Reconciliation checks")
    st.dataframe(runtime.data.quality, width="stretch", hide_index=True)
    st.markdown("#### Source contracts and freshness")
    freshness = runtime.data.source_freshness.copy()
    source_contracts = bundle.settings.source_contracts.model_dump()
    freshness["source_name"] = freshness["source"].map(
        lambda source: source_contracts[source]["display_name"]
    )
    freshness["grain"] = freshness["source"].map(
        lambda source: source_contracts[source]["grain"]
    )
    freshness["refresh_cadence"] = freshness["source"].map(
        lambda source: source_contracts[source]["refresh_cadence"]
    )
    st.dataframe(
        freshness[["source_name", "grain", "refresh_cadence", "last_refresh", "age_hours", "sla_hours", "status", "row_count"]],
        width="stretch",
        hide_index=True,
        column_config={
            "source_name": "Source",
            "grain": "Source grain",
            "refresh_cadence": "Simulated refresh cadence",
            "last_refresh": "Last refresh",
            "age_hours": st.column_config.NumberColumn("Age (hours)", format="%.1f"),
            "sla_hours": st.column_config.NumberColumn("Freshness SLA (hours)", format="%.1f"),
            "status": "Freshness",
            "row_count": st.column_config.NumberColumn("Rows", format="%d"),
        },
    )

with tab_eval:
    st.markdown("#### Predefined acceptance scenarios")
    display = runtime.evaluation.copy()
    display["result"] = display["passed"].map({True: "PASS", False: "FAIL"})
    st.dataframe(display[["scenario_id", "scenario", "expected", "actual", "matched_finding", "result"]], width="stretch", hide_index=True)
    st.caption("Ground-truth labels are read only by the evaluation module after analytics complete. The analytical pipeline cannot access them.")

with tab_benchmark:
    st.markdown("#### Four-method baseline comparison")
    benchmark = runtime.benchmark.copy()
    metric_view = benchmark.melt(
        id_vars=["method"],
        value_vars=["precision", "recall", "f1"],
        var_name="metric",
        value_name="score",
    )
    figure = px.bar(
        metric_view,
        x="method",
        y="score",
        color="metric",
        barmode="group",
        color_discrete_map={"precision": "#6558e8", "recall": "#28b99a", "f1": "#e7ad2f"},
    )
    figure.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=28, b=65),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", color="#5f6b80"),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Score", range=[0, 1.05], tickformat=".0%", gridcolor="#edf0f5", zeroline=False),
        xaxis=dict(title=None),
    )
    figure.update_traces(hovertemplate="%{x}<br>%{data.name}: <b>%{y:.0%}</b><extra></extra>")
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})
    st.dataframe(
        benchmark,
        width="stretch",
        hide_index=True,
        column_config={
            "precision": st.column_config.NumberColumn("Precision", format="%.0%%"),
            "recall": st.column_config.NumberColumn("Recall", format="%.0%%"),
            "f1": st.column_config.NumberColumn("F1", format="%.0%%"),
            "false_positive_cost_inr": st.column_config.NumberColumn("Illustrative FP cost", format="₹%,.0f"),
            "driver_ranking_accuracy": st.column_config.NumberColumn("Driver accuracy", format="%.0%%"),
            "abstention_correctness": st.column_config.NumberColumn("Abstention", format="%.0%%"),
            "narrative_numerical_accuracy": st.column_config.NumberColumn("Narrative numeric", format="%.0%%"),
            "evaluation_latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%.2f"),
        },
    )
    st.caption("Alert-class metrics use the four analytical scenarios. The false-positive review cost is an explicit demonstration assumption of ₹250,000 per unnecessary investigation—not a regulatory or bank cost estimate.")
    with st.expander("Scenario-level predictions"):
        st.dataframe(runtime.benchmark_detail, width="stretch", hide_index=True)

with tab_security:
    st.markdown("#### Pre-evidence entitlement test")
    west_user = get_user("west_investigator", bundle)
    decision = check_access(west_user, "NORTH", detail=True)
    st.code("west_investigator → request NORTH entity detail", language="text")
    if decision.allowed:
        st.error("Unexpectedly allowed")
    else:
        render_decision_banner(
            "ALERT",
            "Access denied before evidence construction",
            decision.reason,
        )
    if st.button("Record security test"):
        record_security(PROJECT_ROOT, west_user.id, "NORTH", "ACCESS_DENIED" if not decision.allowed else "ALLOWED", decision.reason)
        st.success("Security event recorded without constructing restricted evidence.")
    events = read_events(PROJECT_ROOT, "security_events", 20)
    if not events.empty:
        st.dataframe(events[["created_at", "user_id", "requested_region", "outcome", "reason"]], width="stretch", hide_index=True)

with tab_runtime:
    telemetry = read_events(PROJECT_ROOT, "runtime_events", 25)
    if telemetry.empty:
        st.caption("No runtime events recorded.")
    else:
        latest = telemetry.iloc[0]
        metrics = st.columns(5)
        metrics[0].metric("End-to-end latency", f"{latest['latency_ms']:,.0f} ms")
        metrics[1].metric("Model calls", int(latest["model_calls"]))
        metrics[2].metric("Tokens", f"{int(latest['tokens']):,}")
        metrics[3].metric("Estimated cost", f"US${latest['estimated_cost_usd']:,.4f}")
        metrics[4].metric("Cache", str(latest["cache_status"]).title())
        st.markdown("#### Recent execution telemetry")
        st.dataframe(telemetry, width="stretch", hide_index=True)
    st.markdown("#### LLM versus non-LLM processing boundary")
    deterministic, narrative = st.columns(2)
    with deterministic:
        with st.container(border=True):
            st.markdown("##### Deterministic processing · executed")
            st.markdown(
                "- Source validation, reconciliation, and freshness\n"
                "- KPI calculation, baselines, materiality, and driver reconciliation\n"
                "- Transparent NetworkX relationships and review scoring\n"
                "- Evidence confidence, abstention, authorization, and action selection"
            )
            st.success("These stages own every number, score, threshold, and permitted action.")
    with narrative:
        with st.container(border=True):
            st.markdown("##### Narrative layer · disabled in this run")
            st.markdown(
                "- Current output uses the deterministic evidence-linked fallback\n"
                "- If enabled, an LLM may only convert the validated packet into persona-specific language\n"
                "- It may not calculate KPIs, confidence, contributions, or select actions\n"
                "- Raw identifiers remain excluded before any narrative call"
            )
            st.info(
                f"LLM enabled: {bundle.settings.llm.enabled} · "
                f"Raw identifiers allowed: {bundle.settings.security.send_raw_identifiers_to_llm}"
            )

with tab_feedback:
    finding_options = runtime.analysis.findings.loc[runtime.analysis.findings["region"].eq(region), "finding_id"].tolist()
    if not finding_options:
        st.caption("No findings are available for feedback in this region.")
    else:
        with st.form("feedback_form"):
            finding_id = st.selectbox("Finding", finding_options)
            rating = st.radio("Was this explanation useful?", ["Useful", "Partly useful", "Not useful"], horizontal=True)
            correctness = st.radio("Was the explanation correct?", ["Correct", "Partially correct", "Incorrect"], horizontal=True)
            corrected_driver = st.text_input("Corrected primary driver (if needed)")
            action_decision = st.radio("Recommended action", ["Accepted", "Rejected", "Not reviewed"], horizontal=True)
            comment = st.text_area("Comment", placeholder="What evidence or explanation was missing?")
            submitted = st.form_submit_button("Submit feedback", type="primary")
            if submitted:
                record_feedback(PROJECT_ROOT, user.id, finding_id, rating, comment, correctness, corrected_driver, action_decision, user.role)
                st.success("Feedback saved for governance review.")
        feedback = read_events(PROJECT_ROOT, "feedback_events", 20)
        if not feedback.empty:
            st.dataframe(feedback[["created_at", "user_id", "user_role", "finding_id", "correctness", "corrected_driver", "action_decision", "rating", "comment"]], width="stretch", hide_index=True)
