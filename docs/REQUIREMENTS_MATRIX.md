# Round 2 Requirements Matrix

| Requirement | Implementation | Demo proof | Status |
|---|---|---|---|
| 3–5 connected KPIs | Five governed KPI contracts plus an explicit operational relationship map | Command Center + KPI Pulse | Complete |
| 2–3 heterogeneous sources | Transactions, KYC, cases | Command Center source readiness | Complete |
| Different grains/cadences | Transaction event/15-minute, account snapshot/daily, case event/four-hour governed source contracts | Source readiness + Governance | Complete |
| Semantic contract | YAML formula, constraints, drivers, materiality, minimum history, lineage, and role access | KPI Pulse contract drawer | Complete |
| Multi-factor movement | Injected region/account/channel/relationship drivers | Contribution chart | Complete |
| Two personas | Compliance Head and Regional Investigator | Persona switch | Complete |
| Low-confidence scenario | Stale KYC and missing mappings | Abstention | Complete |
| Sparse-history scenario | Fourteen-day new channel | Peer-based label | Complete |
| Role-based security | Region and detail entitlements | Access-denied scenario | Complete |
| Evidence/freshness/method | Evidence IDs, source freshness, analytical method, contributions, confidence, and visible lineage | Investigation evidence + Why It Changed | Complete |
| LLM/non-LLM separation | Human-readable deterministic-versus-narrative boundary with explicit prohibited LLM tasks | Governance runtime + execution trace | Complete |
| Recommended actions | Governed action playbooks | Action Workspace | Complete |
| Feedback loop | SQLite feedback events | Governance page | Complete |
| Runtime telemetry | Live cards and history for latency, calls, tokens, estimated cost, and cache | Governance runtime | Complete |
| Held-out evaluation | Ground truth and baseline comparison | Evaluation panel | Complete |
| Exact KPI hand checks | 10-row examples and expected results for all five formulas | KPI manual verification + tests | Complete |
| Driver reconciliation | Exclusive leaves, contribution percentages, explained/unexplained proof | Why It Changed waterfall | Complete |
| Evidence-only explanation | Structured packet is built after access control and is the only LLM payload | Investigation packet drawer + tests | Complete |
| Evaluation methods | Threshold, movement, movement + proximity, full graph method | Governance method comparison | Complete |
| LLM-disabled operation | Deterministic narratives and zero-call evaluation | Governance runtime + tests | Complete |
| Cross-device readiness | Desktop and 390×844 responsive emulation | Saved screenshots | Emulation complete; physical device pending |
| Public deployment | Streamlit Cloud runbook | `docs/DEPLOYMENT.md` | Owner account step pending |
| Judge submission | Screenshots, deck, owner audit, demo script | Submission pack | Complete |
