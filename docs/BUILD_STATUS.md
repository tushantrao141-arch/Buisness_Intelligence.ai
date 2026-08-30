# SilentSignal — Build Status & Architecture Health

## Project Overview
- **Project Name:** SilentSignal (Milestone 1 — 7-Day Prototype)
- **Problem Statement:** Banking compliance & financial-crime risk intelligence platform
- **Core Principle:** Deterministic analytics (KPIs, Graph, Movement, Drivers, Confidence, Permissions) + Optional Governed LLM narrative layer.

## Architecture Health Checklist (exec.md Compliance)

| Area | Status | Notes |
|---|---|---|
| Synthetic Data Sources | ✅ Complete | 3 governed source contracts with visible grain, cadence, freshness, and 90-day deterministic seed-42 history |
| Referential Integrity | ✅ Complete | Transactions -> KYC (100% match), Cases -> KYC/Accounts (100% match) |
| Governed KPIs (5/5) | ✅ Complete | Formula, constraints, drivers, materiality, lineage, minimum history, and role access are machine-readable and visible in the app |
| Movement & Baselines | ✅ Complete | 28-day governed mean/standard-deviation baseline with config-driven KPI materiality gates |
| Relationship Graph | ✅ Complete | NetworkX shared phone/address/beneficiary graph with review-score, near-event, and 50% active-account coverage gates |
| Driver Reconciliation | ✅ Complete | Mutually exclusive leaf-segment contributions reconciling exactly to movement |
| Evidence & Confidence | ✅ Complete | Transparent quality score, S3 abstention gate, evidence IDs, and visible calculation lineage |
| RBAC & Security | ✅ Complete | Pre-evidence access check, region filtering, identifier masking |
| Governed Actions | ✅ Complete | Triggered from action playbooks by role, no autonomous execution |
| Telemetry & Audit | ✅ Complete | Visible latency, model calls, tokens, estimated cost, cache status, plus SQLite action/feedback/security events |
| Evaluation Benchmark | ✅ Complete | Predefined S1–S5 acceptance diagnostics, 4-method comparison |
| Decision Workspace | ✅ Complete | 5 professional Streamlit pages, connected-KPI map, readable LLM boundary, and cross-page persona/region context |

## Verification Checkpoint

- **66 tests passing** after the judge-readiness contract and UI update.
- Project configuration validation passes.
- All six Streamlit surfaces render through automated smoke tests.
- Physical mobile-device testing and owner-account public deployment remain external owner steps.

## Acceptance Scenarios (S1–S5)
- **S1 (Strong connected pattern — WEST):** ALERT (confidence >= 0.75)
- **S2 (Legitimate seasonal activity — EAST):** MONITOR (confidence 0.84, expected-turnover match)
- **S3 (Insufficient evidence — NORTH):** ABSTAIN (confidence < 0.60, missing mapping/stale KYC)
- **S4 (Sparse-history channel — SOUTH):** PEER_BASED (14-day history capped with peer branches)
- **S5 (Unauthorised region access):** ACCESS_DENIED (Pre-evidence authorization enforcement)
