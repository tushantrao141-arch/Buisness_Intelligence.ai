"""Shared Streamlit presentation and interaction helpers."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

from src.config import load_config_bundle
from src.runtime import build_demo
from src.schemas import KPIContract
from src.security import allowed_regions


STATUS_COLOURS = {
    "ALERT": ("#fff0ee", "#b9382f", "#e85b50"),
    "ABSTAIN": ("#fff7df", "#8a6100", "#e7ad2f"),
    "PEER_BASED": ("#eef4ff", "#315fa8", "#5b8def"),
    "MONITOR": ("#eaf8f3", "#16705b", "#26a987"),
}


def configure_page(title: str, icon: str = "🔎") -> None:
    """Set page metadata and load the shared SilentSignal visual system."""

    st.set_page_config(
        page_title=f"{title} | SilentSignal",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
          :root {
            --ss-bg: #f3f6fb;
            --ss-surface: #ffffff;
            --ss-surface-soft: #f8f9fd;
            --ss-ink: #102036;
            --ss-muted: #66748a;
            --ss-line: #e1e7f0;
            --ss-primary: #6558e8;
            --ss-primary-dark: #493bbf;
            --ss-aqua: #28b99a;
            --ss-navy: #101b31;
            --ss-danger: #e85b50;
            --ss-warning: #e7ad2f;
            --ss-shadow: 0 18px 50px rgba(25, 43, 78, .08);
          }

          html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", ui-sans-serif, system-ui, -apple-system, sans-serif;
          }
          .stApp {
            color: var(--ss-ink);
            background:
              radial-gradient(circle at 88% 4%, rgba(101,88,232,.09), transparent 24rem),
              linear-gradient(180deg, #f8faff 0%, var(--ss-bg) 32%, #f7f9fc 100%);
          }
          header[data-testid="stHeader"] { background: transparent; }
          [data-testid="stToolbar"] { right: 1.2rem; }
          .block-container {
            max-width: 1480px;
            padding-top: 1.35rem;
            padding-bottom: 4rem;
          }
          h1, h2, h3, h4 {
            color: var(--ss-ink);
            letter-spacing: -.035em;
          }
          h1 { font-size: clamp(2.2rem, 4vw, 3.65rem); line-height: 1.04; }
          h2 { font-size: 1.65rem; }
          h3 { font-size: 1.18rem; }
          p { line-height: 1.65; }
          hr { border-color: var(--ss-line); }

          [data-testid="stSidebar"] {
            background:
              radial-gradient(circle at 30% 5%, rgba(101,88,232,.32), transparent 14rem),
              linear-gradient(180deg, #111a30 0%, #0d1628 58%, #0a1323 100%);
            border-right: 1px solid rgba(255,255,255,.08);
          }
          [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
          [data-testid="stSidebar"] * { color: #eef2ff; }
          [data-testid="stSidebar"] p,
          [data-testid="stSidebar"] label { color: #b9c3da !important; }
          [data-testid="stSidebarNav"] { display: none; }
          [data-testid="stSidebarNav"] span { font-weight: 650; }
          [data-testid="stSidebarNav"] a {
            border-radius: 11px;
            margin: 2px 8px;
            transition: background .2s ease, transform .2s ease;
          }
          [data-testid="stSidebarNav"] a:hover {
            background: rgba(255,255,255,.08);
            transform: translateX(2px);
          }
          [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: rgba(255,255,255,.07);
            border-color: rgba(255,255,255,.14);
            border-radius: 11px;
          }
          [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            background: transparent;
            border: 0;
            border-radius: 10px;
            color: #c4cde0;
            justify-content: flex-start;
            min-height: 38px;
            padding: 7px 9px;
            width: 100%;
          }
          [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: rgba(255,255,255,.075);
            box-shadow: none;
            color: white;
            transform: translateX(2px);
          }
          .ss-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 8px 18px;
          }
          .ss-brand-mark {
            width: 42px;
            height: 42px;
            display: grid;
            place-items: center;
            border-radius: 13px;
            color: white;
            font-size: 1.1rem;
            font-weight: 850;
            background: linear-gradient(145deg, #8579ff, #4f42cf);
            box-shadow: 0 10px 30px rgba(101,88,232,.38);
          }
          .ss-brand-name { color: white; font-size: 1.08rem; font-weight: 800; line-height: 1.1; }
          .ss-brand-sub { color: #9eabc7; font-size: .71rem; letter-spacing: .09em; margin-top: 4px; text-transform: uppercase; }
          .ss-sidebar-label {
            color: #7f8ba5;
            font-size: .67rem;
            font-weight: 800;
            letter-spacing: .13em;
            margin: 12px 2px 5px;
            text-transform: uppercase;
          }
          .ss-scope-card {
            background: rgba(255,255,255,.055);
            border: 1px solid rgba(255,255,255,.10);
            border-radius: 14px;
            margin-top: 14px;
            padding: 13px 14px;
          }
          .ss-scope-card strong { color: white; font-size: .86rem; }
          .ss-scope-row { display: flex; justify-content: space-between; gap: 12px; margin-top: 8px; color: #aeb9d1; font-size: .76rem; }
          .ss-sidebar-live { display: flex; align-items: center; gap: 7px; color: #8edbc8; font-size: .73rem; margin-top: 13px; }
          .ss-live-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #37d6ad;
            box-shadow: 0 0 0 5px rgba(55,214,173,.10);
          }

          [data-testid="stMetric"] {
            min-height: 126px;
            background: rgba(255,255,255,.92);
            border: 1px solid var(--ss-line);
            border-radius: 17px;
            padding: 18px 19px;
            box-shadow: 0 10px 28px rgba(31,46,78,.055);
            overflow: hidden;
            position: relative;
            transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
          }
          [data-testid="stMetric"]:hover {
            border-color: #d4d9ef;
            box-shadow: var(--ss-shadow);
            transform: translateY(-2px);
          }
          [data-testid="stMetric"]:before {
            background: linear-gradient(90deg, var(--ss-primary), var(--ss-aqua));
            content: "";
            height: 3px;
            left: 18px;
            position: absolute;
            top: 0;
            width: 34px;
          }
          [data-testid="stMetricLabel"] p {
            color: #758197;
            font-size: .72rem;
            font-weight: 760;
            letter-spacing: .055em;
            text-transform: uppercase;
          }
          [data-testid="stMetricValue"] {
            color: var(--ss-ink);
            font-size: clamp(1.45rem, 2vw, 2.05rem);
            font-weight: 760;
            letter-spacing: -.04em;
          }

          div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,.9);
            border-color: var(--ss-line);
            border-radius: 18px;
            box-shadow: 0 9px 28px rgba(31,46,78,.045);
            transition: border-color .2s ease, box-shadow .2s ease;
          }
          div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #d3d9e6;
            box-shadow: 0 18px 42px rgba(31,46,78,.07);
          }
          [data-testid="stPlotlyChart"] {
            overflow: hidden;
            background: white;
            border: 1px solid var(--ss-line);
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(31,46,78,.045);
            padding: 6px;
          }
          [data-testid="stDataFrame"] {
            border: 1px solid var(--ss-line);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(31,46,78,.04);
          }
          [data-testid="stExpander"] {
            background: rgba(255,255,255,.78);
            border-color: var(--ss-line);
            border-radius: 14px;
          }
          [data-baseweb="tab-list"] {
            gap: 7px;
            background: #e9edf5;
            border-radius: 13px;
            padding: 5px;
          }
          [data-baseweb="tab"] {
            border-radius: 9px;
            color: #5f6b80;
            font-weight: 680;
            padding: 9px 14px;
          }
          [aria-selected="true"][data-baseweb="tab"] {
            color: var(--ss-ink);
            background: white;
            box-shadow: 0 3px 12px rgba(21,33,58,.08);
          }
          [data-baseweb="tab-highlight"] { display: none; }
          .stButton > button,
          .stFormSubmitButton > button,
          [data-testid="stPageLink"] a {
            min-height: 42px;
            border-radius: 11px;
            border: 1px solid #d9deea;
            font-weight: 720;
            transition: transform .18s ease, box-shadow .18s ease;
          }
          .stButton > button:hover,
          .stFormSubmitButton > button:hover,
          [data-testid="stPageLink"] a:hover {
            border-color: var(--ss-primary);
            box-shadow: 0 8px 22px rgba(101,88,232,.13);
            transform: translateY(-1px);
          }
          button[kind="primary"] {
            color: white !important;
            border: 0 !important;
            background: linear-gradient(135deg, var(--ss-primary), var(--ss-primary-dark)) !important;
          }
          [data-testid="stAlert"] { border-radius: 14px; }
          [data-testid="stSelectbox"] [data-baseweb="select"] > div,
          [data-testid="stTextInput"] input,
          [data-testid="stTextArea"] textarea {
            background: white;
            border-color: #dce2eb;
            border-radius: 11px;
          }

          .ss-eyebrow {
            color: var(--ss-primary);
            font-size: .70rem;
            font-weight: 820;
            letter-spacing: .15em;
            text-transform: uppercase;
          }
          .ss-page-header {
            align-items: end;
            display: flex;
            gap: 24px;
            justify-content: space-between;
            margin: 2px 0 14px;
            padding: 4px 2px 2px;
          }
          .ss-page-header h1 {
            font-size: clamp(2.05rem, 3.5vw, 3.15rem);
            margin: 7px 0 8px;
          }
          .ss-page-header p { color: var(--ss-muted); font-size: 1.02rem; margin: 0; max-width: 780px; }
          .ss-page-tag {
            align-items: center;
            background: white;
            border: 1px solid var(--ss-line);
            border-radius: 999px;
            color: #536079;
            display: inline-flex;
            flex: none;
            font-size: .74rem;
            font-weight: 720;
            gap: 8px;
            margin-bottom: 5px;
            padding: 8px 12px;
            box-shadow: 0 6px 18px rgba(31,46,78,.05);
          }
          .ss-page-tag:before { background: var(--ss-aqua); border-radius: 50%; content: ""; height: 7px; width: 7px; }

          .ss-system-strip {
            align-items: center;
            background: rgba(255,255,255,.78);
            border: 1px solid var(--ss-line);
            border-radius: 13px;
            color: #6c778c;
            display: flex;
            flex-wrap: wrap;
            font-size: .72rem;
            gap: 8px 17px;
            margin-bottom: 22px;
            padding: 9px 13px;
          }
          .ss-system-item { align-items: center; display: flex; gap: 6px; }
          .ss-system-item strong { color: #34425a; }
          .ss-system-dot { background: var(--ss-aqua); border-radius: 50%; height: 6px; width: 6px; }

          .ss-hero {
            background:
              radial-gradient(circle at 92% 12%, rgba(92,229,197,.17), transparent 22rem),
              radial-gradient(circle at 68% 100%, rgba(132,117,255,.32), transparent 23rem),
              linear-gradient(120deg, #0e1a31 0%, #17264a 55%, #352c80 100%);
            border: 1px solid rgba(255,255,255,.1);
            border-radius: 26px;
            box-shadow: 0 28px 80px rgba(22,31,66,.22);
            color: white;
            display: grid;
            gap: 34px;
            grid-template-columns: minmax(0, 1.65fr) minmax(280px, .72fr);
            margin: 1px 0 16px;
            overflow: hidden;
            padding: clamp(26px, 4vw, 48px);
            position: relative;
          }
          .ss-hero:after {
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 50%;
            content: "";
            height: 270px;
            position: absolute;
            right: -70px;
            top: -120px;
            width: 270px;
          }
          .ss-hero h1 { color: white; font-size: clamp(2.45rem, 4.8vw, 4.45rem); margin: 11px 0 17px; max-width: 900px; }
          .ss-hero p { color: #c9d2e7; font-size: clamp(.98rem, 1.35vw, 1.12rem); margin: 0; max-width: 750px; }
          .ss-hero .ss-eyebrow { color: #9df0dc; }
          .ss-hero-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 24px; }
          .ss-hero-pill {
            background: rgba(255,255,255,.08);
            border: 1px solid rgba(255,255,255,.13);
            border-radius: 999px;
            color: #e1e7f6;
            font-size: .73rem;
            font-weight: 650;
            padding: 7px 11px;
          }
          .ss-hero-panel {
            align-self: stretch;
            backdrop-filter: blur(16px);
            background: rgba(255,255,255,.075);
            border: 1px solid rgba(255,255,255,.13);
            border-radius: 18px;
            padding: 20px;
            position: relative;
            z-index: 1;
          }
          .ss-panel-label { color: #aab7d4; font-size: .68rem; font-weight: 780; letter-spacing: .12em; text-transform: uppercase; }
          .ss-panel-value { color: white; font-size: 2.7rem; font-weight: 780; letter-spacing: -.06em; margin: 7px 0 1px; }
          .ss-panel-note { color: #aebad3; font-size: .76rem; }
          .ss-signal-row { align-items: center; border-top: 1px solid rgba(255,255,255,.1); display: flex; justify-content: space-between; margin-top: 16px; padding-top: 14px; }
          .ss-signal-row span { color: #b9c5db; font-size: .74rem; }
          .ss-signal-row strong { color: white; font-size: .82rem; }

          .ss-section-header { align-items: end; display: flex; justify-content: space-between; margin: 30px 1px 13px; }
          .ss-section-header h2 { font-size: 1.42rem; margin: 3px 0 0; }
          .ss-section-header p { color: var(--ss-muted); font-size: .82rem; margin: 0; max-width: 550px; text-align: right; }
          .ss-muted { color: var(--ss-muted); }
          .ss-chip {
            align-items: center;
            border: 1px solid currentColor;
            border-radius: 999px;
            display: inline-flex;
            font-size: .69rem;
            font-weight: 790;
            gap: 6px;
            letter-spacing: .045em;
            margin-right: 6px;
            padding: 5px 9px;
            text-transform: uppercase;
          }
          .ss-chip-dot { background: currentColor; border-radius: 50%; height: 6px; width: 6px; }
          .ss-finding-card {
            background: white;
            border: 1px solid var(--ss-line);
            border-left: 4px solid var(--ss-accent, var(--ss-primary));
            border-radius: 17px;
            box-shadow: 0 10px 28px rgba(31,46,78,.05);
            display: grid;
            gap: 16px;
            grid-template-columns: minmax(0, 1fr) 170px;
            margin-bottom: 11px;
            padding: 18px 20px;
          }
          .ss-finding-card h3 { font-size: 1.02rem; margin: 8px 0 4px; }
          .ss-finding-card p { color: #66748a; font-size: .82rem; margin: 0; }
          .ss-finding-meta { color: #8893a6; font-size: .70rem; margin-top: 8px; }
          .ss-confidence { align-self: center; text-align: right; }
          .ss-confidence strong { display: block; font-size: 1.48rem; letter-spacing: -.04em; }
          .ss-confidence span { color: #7d889d; font-size: .68rem; font-weight: 700; text-transform: uppercase; }
          .ss-confidence-track { background: #edf0f5; border-radius: 999px; height: 6px; margin-top: 9px; overflow: hidden; }
          .ss-confidence-fill { background: var(--ss-accent, var(--ss-primary)); border-radius: 999px; height: 100%; }

          .ss-evidence {
            background: #f8f7ff;
            border: 1px solid #e8e5ff;
            border-left: 3px solid var(--ss-primary);
            border-radius: 0 12px 12px 0;
            color: #4f5e76;
            font-size: .86rem;
            margin: 7px 0;
            padding: 13px 15px;
          }
          .ss-evidence strong { color: #302778; }
          .ss-decision-banner {
            align-items: center;
            background: var(--ss-decision-bg);
            border: 1px solid var(--ss-decision-accent);
            border-radius: 16px;
            display: flex;
            gap: 14px;
            margin: 13px 0 20px;
            padding: 15px 17px;
          }
          .ss-decision-icon {
            align-items: center;
            background: var(--ss-decision-accent);
            border-radius: 11px;
            color: white;
            display: flex;
            flex: none;
            font-weight: 850;
            height: 38px;
            justify-content: center;
            width: 38px;
          }
          .ss-decision-banner strong { color: var(--ss-ink); display: block; font-size: .88rem; }
          .ss-decision-banner span { color: #66748a; font-size: .78rem; }

          .ss-flow { display: grid; gap: 10px; grid-template-columns: repeat(5, 1fr); }
          .ss-flow-step {
            background: white;
            border: 1px solid var(--ss-line);
            border-radius: 15px;
            min-height: 128px;
            padding: 16px;
            position: relative;
          }
          .ss-flow-step:not(:last-child):after {
            color: #aeb6c5;
            content: "→";
            font-size: 1rem;
            position: absolute;
            right: -10px;
            top: 46%;
            z-index: 2;
          }
          .ss-flow-number { color: var(--ss-primary); font-size: .68rem; font-weight: 820; letter-spacing: .09em; }
          .ss-flow-title { color: var(--ss-ink); font-size: .91rem; font-weight: 780; margin: 8px 0 5px; }
          .ss-flow-detail { color: #758197; font-size: .72rem; line-height: 1.5; }
          .ss-kpi-map {
            align-items: center;
            display: grid;
            gap: 12px;
            grid-template-columns: 1fr auto 1fr auto 1fr auto 1.25fr;
          }
          .ss-kpi-node {
            background: linear-gradient(145deg, #fff, #f7f6ff);
            border: 1px solid #e5e2f8;
            border-radius: 15px;
            min-height: 112px;
            padding: 16px;
          }
          .ss-kpi-node strong { color: var(--ss-ink); display: block; font-size: .86rem; line-height: 1.3; }
          .ss-kpi-node span { color: #778399; display: block; font-size: .69rem; line-height: 1.45; margin-top: 8px; }
          .ss-kpi-order { color: var(--ss-primary) !important; font-size: .62rem !important; font-weight: 820; letter-spacing: .09em; margin: 0 0 7px !important; text-transform: uppercase; }
          .ss-kpi-arrow { color: #a7a0dd; font-size: 1.35rem; font-weight: 800; }
          .ss-kpi-outcomes { display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }
          .ss-health-grid { display: grid; gap: 10px; grid-template-columns: repeat(3, 1fr); }
          .ss-health-card { background: white; border: 1px solid var(--ss-line); border-radius: 14px; padding: 14px; }
          .ss-health-top { align-items: center; display: flex; justify-content: space-between; }
          .ss-health-name { color: var(--ss-ink); font-size: .82rem; font-weight: 760; }
          .ss-health-state { color: #168064; font-size: .66rem; font-weight: 760; text-transform: uppercase; }
          .ss-health-meta { color: #7c889b; font-size: .70rem; margin-top: 7px; }

          @media (max-width: 980px) {
            .ss-hero { grid-template-columns: 1fr; }
            .ss-flow { grid-template-columns: 1fr 1fr; }
            .ss-flow-step:after { display: none; }
            .ss-kpi-map { grid-template-columns: 1fr; }
            .ss-kpi-arrow { text-align: center; transform: rotate(90deg); }
            .ss-health-grid { grid-template-columns: 1fr; }
          }
          @media (max-width: 720px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .ss-page-header { align-items: start; flex-direction: column; gap: 10px; }
            .ss-page-header p { font-size: .92rem; }
            .ss-section-header { align-items: start; flex-direction: column; gap: 5px; }
            .ss-section-header p { text-align: left; }
            .ss-finding-card { grid-template-columns: 1fr; }
            .ss-confidence { text-align: left; }
            .ss-flow { grid-template-columns: 1fr; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(eyebrow: str, title: str, description: str, tag: str = "Live workspace") -> None:
    """Render a consistent executive heading for a workflow page."""

    st.markdown(
        f"""
        <div class="ss-page-header">
          <div>
            <div class="ss-eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(description)}</p>
          </div>
          <div class="ss-page-tag">{escape(tag)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, description: str = "", eyebrow: str = "") -> None:
    """Introduce a page section with optional context and an eyebrow label."""

    label = f'<div class="ss-eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    detail = f"<p>{escape(description)}</p>" if description else ""
    st.markdown(
        f'<div class="ss-section-header"><div>{label}<h2>{escape(title)}</h2></div>{detail}</div>',
        unsafe_allow_html=True,
    )


def render_project_banner() -> None:
    """Show the non-negotiable runtime and data guardrails in a compact strip."""

    bundle = load_config_bundle()
    st.markdown(
        f"""
        <div class="ss-system-strip">
          <div class="ss-system-item"><span class="ss-system-dot"></span><strong>System healthy</strong></div>
          <div class="ss-system-item">Version <strong>{escape(bundle.settings.project.version)}</strong></div>
          <div class="ss-system-item">Data <strong>Synthetic only</strong></div>
          <div class="ss-system-item">Analytics <strong>Deterministic</strong></div>
          <div class="ss-system-item">LLM <strong>{"Enabled" if bundle.settings.llm.enabled else "Off · fallback active"}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_milestone_notice(message: str) -> None:
    """Render a standard informational notice."""

    st.info(message)


@st.cache_resource(show_spinner="Reconciling sources and running governed analytics…")
def get_demo_runtime():
    """Build and cache the deterministic application runtime."""

    return build_demo(Path(__file__).resolve().parents[1])


def render_sidebar():
    """Render persona and region controls with the current entitlement context."""

    bundle = load_config_bundle()
    users_by_id = {item.id: item for item in bundle.users}
    query_user_id = st.query_params.get("persona")
    session_user_id = st.session_state.get("decision_user_id")
    saved_user_id = query_user_id if query_user_id in users_by_id else session_user_id
    if saved_user_id not in users_by_id:
        saved_user_id = "compliance_head" if "compliance_head" in users_by_id else bundle.users[0].id
    saved_user = users_by_id[saved_user_id]
    saved_regions = allowed_regions(saved_user)
    default_region = "WEST" if "WEST" in saved_regions else saved_regions[0]
    query_region = st.query_params.get("region")
    session_region = st.session_state.get("decision_region")
    saved_region = query_region if query_region in saved_regions else session_region
    if saved_region not in saved_regions:
        saved_region = default_region
    navigation_query = {"persona": saved_user_id, "region": saved_region}
    st.sidebar.markdown(
        """
        <div class="ss-brand">
          <div class="ss-brand-mark">S</div>
          <div>
            <div class="ss-brand-name">SilentSignal</div>
            <div class="ss-brand-sub">Risk intelligence</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="ss-sidebar-label">Workspace</div>', unsafe_allow_html=True)
    try:
        st.sidebar.page_link("app.py", label="Command Center", icon="🏠", query_params=navigation_query)
        st.sidebar.page_link("pages/1_KPI_Pulse.py", label="KPI Pulse", icon="📊", query_params=navigation_query)
        st.sidebar.page_link("pages/2_Why_It_Changed.py", label="Why It Changed", icon="🧭", query_params=navigation_query)
        st.sidebar.page_link("pages/3_SilentSignal_Investigation.py", label="Investigation", icon="🔗", query_params=navigation_query)
        st.sidebar.page_link("pages/4_Actions.py", label="Actions", icon="✅", query_params=navigation_query)
        st.sidebar.page_link("pages/5_Governance.py", label="Governance", icon="⚙️", query_params=navigation_query)
    except KeyError:
        # AppTest executes each page without Streamlit's multipage route metadata.
        st.sidebar.caption("Open the complete app to use workspace navigation.")
    st.sidebar.markdown('<div class="ss-sidebar-label">Decision context</div>', unsafe_allow_html=True)
    # Streamlit gives widgets on different pages separate identities, even when
    # their explicit keys match. Include the governed URL context in the widget
    # key so a value remembered on an older page cannot overwrite a new route.
    user_widget_key = f"_decision_user_widget_{saved_user_id}_{saved_region}"
    st.session_state[user_widget_key] = saved_user_id

    def store_user_context() -> None:
        selected_user_id = st.session_state[user_widget_key]
        st.session_state["decision_user_id"] = selected_user_id
        st.query_params["persona"] = selected_user_id
        selected_regions = allowed_regions(users_by_id[selected_user_id])
        selected_region = st.session_state.get("decision_region")
        if selected_region not in selected_regions:
            selected_region = "WEST" if "WEST" in selected_regions else selected_regions[0]
            st.session_state["decision_region"] = selected_region
        st.query_params["region"] = selected_region

    user_id = st.sidebar.selectbox(
        "Acting persona",
        options=list(users_by_id),
        format_func=lambda item_id: users_by_id[item_id].display_name,
        key=user_widget_key,
        on_change=store_user_context,
    )
    st.session_state["decision_user_id"] = user_id
    user = users_by_id[user_id]

    regions = allowed_regions(user)
    region_widget_key = f"_decision_region_widget_{user_id}_{saved_region}"
    st.session_state[region_widget_key] = saved_region

    def store_region_context() -> None:
        selected_region = st.session_state[region_widget_key]
        st.session_state["decision_region"] = selected_region
        st.query_params["region"] = selected_region

    region = st.sidebar.selectbox(
        "Region scope",
        options=regions,
        key=region_widget_key,
        on_change=store_region_context,
    )
    st.session_state["decision_region"] = region
    if st.query_params.get("persona") != user_id:
        st.query_params["persona"] = user_id
    if st.query_params.get("region") != region:
        st.query_params["region"] = region
    detail_access = "Permitted" if user.can_view_entity_detail else "Aggregate only"
    st.sidebar.markdown(
        f"""
        <div class="ss-scope-card">
          <strong>{escape(user.display_name)}</strong>
          <div class="ss-scope-row"><span>Role</span><span>{escape(user.role.replace('_', ' ').title())}</span></div>
          <div class="ss-scope-row"><span>Region</span><span>{escape(region)}</span></div>
          <div class="ss-scope-row"><span>Entity detail</span><span>{detail_access}</span></div>
          <div class="ss-sidebar-live"><span class="ss-live-dot"></span> Governed analytics online</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="ss-sidebar-label">Navigation</div>', unsafe_allow_html=True)
    return bundle, user, region


def format_kpi_value(kpi_id: str, value: float) -> str:
    """Format a KPI using its governed business unit."""

    if kpi_id in {"near_threshold_value_ratio", "alert_investigation_yield"}:
        return f"{value:.1f}%"
    if kpi_id == "linked_pattern_exposure":
        if abs(value) >= 10_000_000:
            return f"₹{value / 10_000_000:.1f} Cr"
        if abs(value) >= 100_000:
            return f"₹{value / 100_000:.1f} L"
        return f"₹{value:,.0f}"
    return f"{value:,.0f}"


def materiality_rule_text(contract: KPIContract) -> str:
    """Render a governed KPI materiality rule in concise business language."""

    rule = contract.materiality
    delta_symbol = "≥" if rule.delta_comparison == "gte" else ">"
    z_symbol = "≥" if rule.z_score_comparison == "gte" else ">"
    delta_label = "Absolute movement" if rule.delta_mode == "absolute" else "Increase"
    z_label = "|Z-score|" if rule.z_score_mode == "absolute" else "Z-score"
    if contract.unit == "percent":
        delta_value = f"{rule.delta_threshold:g} percentage points"
    elif contract.unit == "INR":
        delta_value = format_kpi_value(contract.id, rule.delta_threshold)
    else:
        delta_value = f"{rule.delta_threshold:g}"
    return (
        f"{delta_label} {delta_symbol} {delta_value} "
        f"{rule.combination.upper()} {z_label} {z_symbol} {rule.z_score_threshold:g}"
    )


def decision_chip(decision: str) -> str:
    """Return a compact, accessible HTML decision badge."""

    background, foreground, _ = STATUS_COLOURS.get(decision, ("#eef1f6", "#46536a", "#758197"))
    label = escape(decision.replace("_", " "))
    return (
        f'<span class="ss-chip" style="background:{background};color:{foreground};border-color:{foreground}33">'
        f'<span class="ss-chip-dot"></span>{label}</span>'
    )


def render_finding_card(finding: Any) -> None:
    """Render a decision finding with confidence and traceability context."""

    decision = str(finding.decision)
    _, _, accent = STATUS_COLOURS.get(decision, ("#eef1f6", "#46536a", "#758197"))
    confidence = max(0.0, min(1.0, float(finding.confidence)))
    st.markdown(
        f"""
        <div class="ss-finding-card" style="--ss-accent:{accent}">
          <div>
            {decision_chip(decision)}
            <h3>{escape(str(finding.title))}</h3>
            <p>{escape(str(finding.summary))}</p>
            <div class="ss-finding-meta">{escape(str(finding.finding_type))} · {escape(str(finding.method))}</div>
          </div>
          <div class="ss-confidence">
            <span>Evidence confidence</span>
            <strong>{confidence:.0%}</strong>
            <div class="ss-confidence-track"><div class="ss-confidence-fill" style="width:{confidence:.0%}"></div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_banner(decision: str, title: str, detail: str) -> None:
    """Show an explicit decision state without implying guilt or certainty."""

    background, _, accent = STATUS_COLOURS.get(decision, ("#eef1f6", "#46536a", "#758197"))
    icon = {"ALERT": "!", "ABSTAIN": "—", "PEER_BASED": "≈", "MONITOR": "◉"}.get(decision, "i")
    st.markdown(
        f"""
        <div class="ss-decision-banner" style="--ss-decision-bg:{background};--ss-decision-accent:{accent}">
          <div class="ss-decision-icon">{icon}</div>
          <div><strong>{escape(title)}</strong><span>{escape(detail)}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
