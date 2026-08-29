"""Shared Streamlit presentation and interaction helpers."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.config import load_config_bundle
from src.runtime import build_demo
from src.security import allowed_regions


STATUS_COLOURS = {
    "ALERT": ("#ffd9d5", "#8f1d14"),
    "ABSTAIN": ("#fff0bf", "#745500"),
    "PEER_BASED": ("#dce8ff", "#1e4f96"),
    "MONITOR": ("#def3e6", "#17653a"),
}


def configure_page(title: str, icon: str = "🔎") -> None:
    st.set_page_config(
        page_title=f"{title} | SilentSignal",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
          :root { --ss-ink:#17213a; --ss-purple:#6652e8; --ss-soft:#f6f7fb; }
          .stApp { background: linear-gradient(180deg,#fbfbfe 0%,#ffffff 45%); }
          [data-testid="stSidebar"] { background:#12182a; }
          [data-testid="stSidebar"] * { color:#eef0ff; }
          [data-testid="stMetric"] { background:white; border:1px solid #e7e8f0; border-radius:14px; padding:16px; box-shadow:0 5px 18px rgba(28,35,64,.04); }
          div[data-testid="stVerticalBlockBorderWrapper"] { border-color:#e7e8f0; border-radius:16px; }
          h1,h2,h3 { letter-spacing:-.025em; color:var(--ss-ink); }
          .ss-eyebrow { color:#6652e8; font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
          .ss-hero { padding:22px 24px; border-radius:20px; background:linear-gradient(120deg,#171d31,#2c285c 65%,#4c3ec2); color:white; margin-bottom:18px; }
          .ss-hero h2 { color:white; margin:.2rem 0 .4rem; }
          .ss-hero p { color:#dcdcf5; max-width:860px; margin:0; }
          .ss-chip { display:inline-block; border-radius:999px; padding:4px 9px; font-size:.78rem; font-weight:700; margin-right:6px; }
          .ss-muted { color:#65708a; }
          .ss-evidence { border-left:3px solid #6652e8; padding:8px 12px; background:#f7f6ff; border-radius:0 9px 9px 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_project_banner() -> None:
    bundle = load_config_bundle()
    st.caption(
        f"{bundle.settings.project.name} · v{bundle.settings.project.version} · "
        "Synthetic demo data only · deterministic analytics"
    )


def render_milestone_notice(message: str) -> None:
    st.info(message)


@st.cache_resource(show_spinner="Reconciling sources and running governed analytics…")
def get_demo_runtime():
    return build_demo(Path(__file__).resolve().parents[1])


def render_sidebar():
    bundle = load_config_bundle()
    st.sidebar.markdown("## SilentSignal")
    st.sidebar.caption("KPI intelligence → defensible action")
    user = st.sidebar.selectbox(
        "Acting persona",
        options=list(bundle.users),
        format_func=lambda item: item.display_name,
        key="active_user",
    )
    regions = allowed_regions(user)
    default_region = "WEST" if "WEST" in regions else regions[0]
    region = st.sidebar.selectbox(
        "Region scope",
        options=regions,
        index=regions.index(default_region),
        key=f"active_region_{user.id}",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Role · {user.role.replace('_', ' ').title()}")
    st.sidebar.caption("Entity detail · " + ("Permitted" if user.can_view_entity_detail else "Masked aggregate only"))
    st.sidebar.caption("LLM · Off (deterministic fallback active)")
    return bundle, user, region


def format_kpi_value(kpi_id: str, value: float) -> str:
    if kpi_id in {"near_threshold_value_ratio", "alert_investigation_yield"}:
        return f"{value:.1f}%"
    if kpi_id == "linked_pattern_exposure":
        if abs(value) >= 10_000_000:
            return f"₹{value / 10_000_000:.1f} Cr"
        if abs(value) >= 100_000:
            return f"₹{value / 100_000:.1f} L"
        return f"₹{value:,.0f}"
    return f"{value:,.0f}"


def decision_chip(decision: str) -> str:
    background, foreground = STATUS_COLOURS.get(decision, ("#eceef5", "#39445e"))
    return f'<span class="ss-chip" style="background:{background};color:{foreground}">{decision.replace("_", " ")}</span>'
