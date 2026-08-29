# SilentSignal — Build Status & Architecture Health

## Project Overview
- **Project Name:** SilentSignal (Milestone 1 — 7-Day Prototype)
- **Problem Statement:** Banking compliance & financial-crime risk intelligence platform
- **Core Principle:** Deterministic analytics (KPIs, Graph, Movement, Drivers, Confidence, Permissions) + Optional Governed LLM narrative layer.

## Architecture Health Checklist (exec.md Compliance)

| Area | Status | Notes |
|---|---|---|
| Synthetic Data Sources | ✅ Complete | 3 sources (transactions, kyc, cases) with 90-day history, deterministic seed 42 |
| Referential Integrity | ✅ Complete | Transactions -> KYC (100% match), Cases -> KYC/Accounts (100% match) |
| Governed KPIs (5/5) | ✅ Complete | Near-threshold ratio, Linked-pattern exposure, High-risk cluster count, Alert yield, Case SLA risk |
| Movement & Baselines | ✅ Complete | 28-day governed baseline, median/MAD z-score, materiality gate |
| Relationship Graph | ✅ Complete | NetworkX graph connecting shared phone, address, beneficiary |
| Driver Reconciliation | ✅ Complete | Mutually exclusive leaf-segment contributions reconciling exactly to movement |
| Evidence & Confidence | ✅ Complete | Transparent quality score, S3 abstention gate, evidence packets with evidence IDs |
| RBAC & Security | ✅ Complete | Pre-evidence access check, region filtering, identifier masking |
| Governed Actions | ✅ Complete | Triggered from action playbooks by role, no autonomous execution |
| Telemetry & Audit | ✅ Complete | SQLite local audit store for runtime, action, feedback, security events |
| Evaluation Benchmark | ✅ Complete | Predefined S1–S5 acceptance diagnostics, 4-method comparison |
| Decision Workspace | ✅ Complete | 5 Streamlit pages (KPI Pulse, Why It Changed, Investigation, Actions, Governance) |

## Acceptance Scenarios (S1–S5)
- **S1 (Strong connected pattern — WEST):** ALERT (confidence >= 0.75)
- **S2 (Legitimate seasonal activity — EAST):** MONITOR (confidence 0.84, expected-turnover match)
- **S3 (Insufficient evidence — NORTH):** ABSTAIN (confidence < 0.60, missing mapping/stale KYC)
- **S4 (Sparse-history channel — SOUTH):** PEER_BASED (14-day history capped with peer branches)
- **S5 (Unauthorised region access):** ACCESS_DENIED (Pre-evidence authorization enforcement)
