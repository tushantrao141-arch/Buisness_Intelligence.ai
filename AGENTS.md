# AGENTS.md — SilentSignal

## Purpose

This file is the repository-level operating context for coding agents working on SilentSignal. Read it before planning or changing code.

SilentSignal is a demo-grade **KPI intelligence-to-action application for banking risk operations**. It is being built for the Accenture BusinessIntelligence.ai hackathon. The product must detect material KPI movements and connected activity patterns, rank explanatory drivers, show traceable evidence and data freshness, communicate uncertainty, recommend actions allowed for the current user, and learn from reviewed feedback.

The product must feel like a coherent, evidence-first decision workspace—not a generic dashboard, isolated fraud classifier, or chatbot demo.

Use this priority order when trade-offs occur:

1. Correctness
2. Security and privacy
3. Evidence, explainability, and auditability
4. Reliability and honest uncertainty
5. Maintainability and testability
6. Runtime cost and latency
7. UX polish
8. Cleverness or novelty

Never sacrifice the first five for a visually impressive prototype.

---

## Current Repository Truth

The repository is currently at **Milestone 1: specification and scaffold**.

Implemented:

- product, data, KPI, scenario, and requirements specifications;
- governed YAML configuration;
- strict Pydantic configuration schemas and cross-file validation;
- a five-page Streamlit scaffold;
- initial project/configuration tests;
- 11 verified tests passing at the Milestone 1 checkpoint.

Not yet implemented:

- synthetic-data generation;
- raw or processed datasets;
- data-quality/reconciliation pipeline;
- KPI calculations;
- movement detection;
- relationship graph and review scoring;
- driver contribution analysis;
- evidence-confidence and abstention engines;
- LLM narrative generation;
- SQLite feedback/telemetry;
- held-out evaluation;
- production deployment.

Do not claim that a planned capability exists. Update `docs/BUILD_STATUS.md` only after its code and tests actually pass.

The next expected milestone is deterministic synthetic-data generation with ground-truth scenario injection and data-quality tests.

---

## Sources of Project Truth

Before implementing a task, read the narrowest relevant files:

- `docs/PRODUCT_SPEC.md` — product, users, scope, non-goals, success criteria.
- `docs/DATA_SPEC.md` — source schemas, grains, refresh cadences, and quality rules.
- `docs/KPI_SPEC.md` — business meaning and formulas for the five KPIs.
- `docs/EXPECTED_RESULTS.md` — canonical scenarios and expected alert/monitor/abstain behavior.
- `docs/REQUIREMENTS_MATRIX.md` — hackathon requirement-to-demo mapping.
- `docs/BUILD_STATUS.md` — implemented and planned milestones.
- `docs/7_DAY_EXECUTION_PLAN.md` — research-informed build sequence, architecture refinements, release gates, and demo plan.
- `configs/*.yaml` — machine-readable KPI, action, user, safety, and runtime configuration.
- `src/schemas.py` — strict configuration contracts.
- existing tests — verified behavior that must not regress.

If documentation, configuration, tests, and implementation disagree, do not silently guess. Determine whether the task intentionally changes the contract; otherwise preserve tested behavior and report the mismatch.

---

## Core Business Decision

The product helps a bank compliance team answer:

> Which KPI movement or connected activity pattern should be investigated first, why did it become material, how trustworthy is the explanation, and what is the next permitted action for this user?

Every feature should contribute to this decision or to the trustworthiness, safety, evaluation, or operation of the decision workflow.

---

## Primary Users

### Compliance Head

Needs:

- aggregate exposure and trends;
- regional and business contribution;
- investigation capacity/SLA impact;
- confidence and important evidence gaps;
- management-level actions.

The Compliance Head can see all configured regions but should receive aggregate or masked entity information by default.

### Regional AML Investigator

Needs:

- assigned-region transaction and relationship evidence;
- connected masked accounts/entities;
- timing and branch patterns;
- alternative explanations and missing information;
- case-level investigation steps.

Investigators must never receive another region's restricted details merely because a UI filter was changed.

---

## Canonical Product Journey

Preserve this end-to-end demo story:

1. The Compliance Head opens KPI Pulse.
2. The application prioritizes a material change in Linked-Pattern Exposure or a connected KPI.
3. The user opens “Why It Changed.”
4. The engine shows current value, baseline, delta, ranked contributions, method, and freshness.
5. The user opens SilentSignal Investigation.
6. The application shows a focused relationship pattern with masked entities and supporting evidence.
7. Evidence confidence and alternative hypotheses are visible.
8. Strong evidence produces a governed recommendation; insufficient/contradictory evidence produces abstention.
9. The Investigator receives a more detailed, region-authorized narrative and next steps.
10. Feedback, latency, model usage, cost, and security events are recorded.

Avoid disconnected features that do not strengthen this journey.

---

## Canonical Scenarios

Use stable scenario IDs and preserve their intended outcomes.

### S1 — Strong connected pattern

Eight related new accounts conduct repeated near-threshold cash activity across four branches over fourteen days and share fabricated identifiers/beneficiaries.

Expected outcome: material KPI movement, one connected cluster, ranked multi-factor explanation, high evidence confidence when data is complete/fresh, and persona-appropriate investigation actions.

### S2 — Legitimate seasonal activity

A cash-intensive business experiences expected seasonal activity with fresh KYC and no cross-account relationship.

Expected outcome: show the legitimate alternative hypothesis; do not conclude wrongdoing.

### S3 — Insufficient evidence

Near-threshold activity exists, but KYC is stale, entity mappings are incomplete, and a legitimate explanation is plausible.

Expected outcome: lower confidence, request the missing data, and abstain from high-impact escalation.

### S4 — Sparse-history channel

`NEW_DEPOSIT` has only fourteen days of history.

Expected outcome: use a labeled peer baseline when suitable, cap confidence, and abstain if comparable peers are insufficient.

### S5 — Unauthorized region

A WEST investigator requests NORTH-region details.

Expected outcome: deny access before evidence construction or LLM invocation, and record a security event.

Ground-truth scenario files are for evaluation only. Analytical/detection/narrative modules must never read them.

---

## Five Governed KPIs

Use the exact identifiers in `configs/kpi_contracts.yaml`.

1. `near_threshold_value_ratio` — qualifying near-threshold cash value divided by all relevant cash value in the same slice.
2. `linked_pattern_exposure` — unique transaction value belonging to qualifying connected clusters; never double-count a transaction.
3. `high_risk_cluster_count` — distinct connected clusters above the transparent review-score threshold.
4. `alert_investigation_yield` — confirmed/escalated closed investigations divided by all closed investigated cases; exclude open cases.
5. `case_sla_risk` — open/in-review cases due to breach SLA within the configured horizon.

Rules:

- KPI calculations are deterministic and testable.
- Formulas, thresholds, windows, owners, sources, access, and drivers belong in governed configuration/specifications—not scattered magic numbers.
- Materiality considers both statistical unusualness and business impact.
- Hard-rule overrides must be visible in the evidence.
- Driver contributions must reconcile with the KPI delta; show unexplained residual explicitly.
- Do not describe an association as causal without appropriate intervention evidence.

---

## Domain and Risk Language

SilentSignal is decision support, not an autonomous judge.

Prefer:

- risk signal;
- elevated exposure;
- linked-pattern indicator;
- qualifying review pattern;
- explanatory association;
- requires review;
- evidence is insufficient.

Avoid unsupported conclusions such as:

- customer is fraudulent;
- account is criminal;
- transaction is definitely money laundering.

Near-threshold activity alone is not proof of suspicious or illegal conduct. The configured ₹10 lakh value is an **illustrative prototype threshold**; do not present it as a complete statement of regulatory obligations. Do not fabricate regulatory citations or legal requirements.

Separate:

1. observed facts;
2. derived features;
3. rule/statistical outputs;
4. evidence-confidence result;
5. analyst interpretation;
6. final human disposition.

Use `review_score` for pattern prioritization. Use `evidence_confidence` for trust in the available explanation. Never label either as probability of guilt.

---

## Data Rules

All prototype data must be synthetic, reproducible, and clearly labeled.

Canonical sources:

- `transactions.csv`: transaction grain, simulated 15-minute refresh;
- `kyc.csv`: account/customer snapshot grain, simulated daily refresh;
- `cases.csv`: investigation event grain, simulated four-hour refresh;
- `source_metadata.json`: generated/refresh timestamps, SLAs, counts, schema versions;
- `data/ground_truth/events.csv`: evaluation-only injected scenario labels.

Preserve the schemas in `docs/DATA_SPEC.md` unless the task explicitly changes them.

Data-generation and transformation requirements:

- use a fixed seed (default `42`) unless a test provides another seed;
- use UTC internally and explicit as-of timestamps;
- use INR for monetary values;
- preserve original synthetic transaction IDs through transformations;
- reject duplicate transaction IDs and non-positive amounts;
- quarantine unknown regions;
- retain unmatched accounts with explicit quality flags;
- record freshness and missingness instead of silently imputing away evidence gaps;
- never use future data in historical baselines or evaluation features;
- never expose real PII, credentials, or production data.

Do not invent healthy-looking dashboard results after an ingestion/validation failure.

---

## Analytical Method Boundaries

Prefer the simplest method that is appropriate, transparent, and testable.

Initial methods:

- SQL/Python for reconciliation and KPI calculations;
- robust historical baseline such as median/MAD or same-weekday comparison for movement detection;
- deterministic proximity, persistence, branch, account-age, and shared-identifier features;
- NetworkX connected components for initial relationship clusters;
- arithmetic contribution analysis for additive KPI deltas;
- scikit-learn metrics for held-out precision/recall/F1 and calibration only when a probabilistic model exists;
- rule-based evidence-quality gates for initial abstention, documented as evidence confidence rather than legal truth.

Do not add a graph database, graph neural network, causal-inference framework, vector database, live-streaming system, or complex model unless a measured requirement justifies it and the user approves the scope change.

Avoid data leakage:

- ground truth is never a feature;
- future case dispositions are never available to earlier predictions;
- use time-based train/validation/test splits;
- freeze held-out data before final evaluation.

---

## LLM Boundaries

The LLM is a narrative layer, not the quantitative source of truth.

Allowed uses:

- convert a validated evidence packet into persona-specific language;
- summarize supported drivers and alternative hypotheses;
- explain a governed action from an approved playbook;
- produce structured narrative fields and evidence references.

Forbidden uses:

- calculate KPI values, contributions, confidence, scores, or expected impact;
- infer missing customer facts;
- invent evidence or citations;
- choose actions outside `configs/action_playbooks.yaml`;
- receive unrestricted/raw sensitive identifiers;
- silently make or execute a compliance disposition.

Required flow:

`deterministic analytics -> validated evidence packet -> authorization/redaction -> structured LLM output -> claim/evidence validation -> UI`

Use strict structured output with Pydantic-compatible schemas. Validate evidence IDs and numeric claims. Retry only within a bounded policy, then use a deterministic Jinja2 fallback. The application must remain demonstrable with the LLM disabled.

The configured provider/model is deployment configuration; do not hard-code it into analytical modules.

---

## Security and Privacy

- Enforce authorization before querying restricted detail, building the evidence packet, or calling the LLM.
- Treat the current user selector as a prototype entitlement simulation, not production authentication.
- The Compliance Head has all-region aggregate access; investigators have configured regional detail access.
- Mask account/customer identifiers in UI, logs, screenshots, and LLM context.
- `send_raw_identifiers_to_llm` must remain `false`.
- Never hard-code or commit secrets. Use `.env` locally and Streamlit secrets for deployment; both must remain excluded from Git.
- Do not expose stack traces, credentials, raw PII-like identifiers, or restricted rows in user-facing errors.
- Record material security denials and feedback/action events when telemetry is implemented.
- Never weaken a safety or entitlement check merely to make the demo work.

---

## Architecture and Repository Map

Keep the 7–8 day prototype as one modular Python/Streamlit application. Do not introduce a separate API or microservice without a demonstrated need.

Technology direction:

- Python 3.11+;
- Streamlit UI;
- Pandas/NumPy data processing;
- DuckDB querying and Parquet processed data;
- Plotly charts;
- NetworkX relationship analysis;
- scikit-learn evaluation;
- YAML governed configuration;
- Pydantic validation;
- Jinja2 narrative fallback;
- SQLite feedback/telemetry;
- OpenAI Responses API for narrative only;
- unittest/Pytest-compatible tests.

Repository responsibilities:

- `app.py` — Streamlit entry point; no quantitative business logic.
- `pages/` — presentation/workflow pages; call services rather than reimplementing calculations.
- `src/schemas.py` — strict data/config/evidence/output contracts.
- `src/config.py` — configuration loading and cross-file validation.
- future `src/data_generator.py` — deterministic synthetic datasets and scenario injection.
- future `src/data_quality.py` — validation/reconciliation/freshness reporting.
- future `src/kpi_engine.py` — deterministic KPI computation.
- future analytical modules — movement, graph, drivers, confidence, evidence, action, narrative, security, telemetry.
- `configs/` — governed non-secret business configuration.
- `data/raw/` — generated source-like CSV/JSON files.
- `data/processed/` — validated/reconciled Parquet files.
- `data/ground_truth/` — evaluation-only labels.
- `artifacts/` — generated evaluation, feedback, and telemetry outputs.
- `tests/` — unit, contract, integration, security, and scenario tests.
- `docs/` — product/data/KPI/scenario/requirements/build contracts.

Business logic must not be embedded in Streamlit page files. UI modules should render results supplied by typed service functions.

---

## Coding Conventions

- Preserve the existing modular structure and naming.
- Use Python type hints and concise docstrings for public modules/functions.
- Prefer small pure functions for calculations and transformations.
- Use `pathlib.Path` for filesystem paths.
- Use strict Pydantic models at configuration, evidence, and LLM boundaries.
- Reject unexpected fields where silent acceptance could hide a contract mismatch.
- Keep timestamps timezone-aware and normalize to UTC.
- Avoid hidden mutable global state.
- Seed any necessary randomness.
- Make empty inputs, missing columns, zero denominators, stale sources, and duplicate IDs explicit cases.
- Do not catch broad exceptions unless adding safe context and preserving the original cause.
- Do not add production dependencies without a clear need; update `requirements.txt` when an approved dependency is added.
- Do not reformat or refactor unrelated files during a feature task.
- Do not delete tests or weaken assertions to make changes pass.

---

## UI Principles

The five canonical pages are:

1. KPI Pulse — prioritization, impact, confidence, and freshness.
2. Why It Changed — baseline, delta, ranked drivers, residual, and alternatives.
3. SilentSignal Investigation — focused relationship graph/table, timing, evidence, and quality gaps.
4. Actions — persona-specific governed recommendation, owner, impact basis, confidence, and monitoring plan.
5. Governance — feedback, security events, methods, model calls, tokens, cost, latency, cache, and evaluation.

Prefer a clear investigation path over decorative charts. Do not render an unbounded graph; start with a selected cluster and focused 1-hop neighborhood. Every number and claim must trace back to computed data/evidence.

---

## Testing and Validation

Run the narrowest relevant tests during development and the complete verified checks before declaring a milestone complete.

Current baseline commands from the repository root:

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
python -m compileall -q app.py pages src scripts tests
```

When Streamlit and all dependencies are installed:

```bash
streamlit run app.py
```

For future analytical features, add tests for:

- hand-verifiable KPI formulas and zero-denominator behavior;
- no double-counting of transaction IDs;
- deterministic output for fixed seeds;
- scenario injection and separation of ground truth;
- source freshness and missing-data gates;
- time-window boundaries and no future leakage;
- graph construction and evidence-preserving edges;
- contribution reconciliation;
- sparse-history peer labeling;
- abstention under insufficient/contradictory evidence;
- authorization before evidence/LLM construction;
- narrative evidence IDs, numeric grounding, and deterministic fallback;
- baseline versus SilentSignal precision/recall/F1;
- feedback and telemetry persistence.

Do not claim a UI smoke test passed when Streamlit was unavailable. Do not claim tests passed unless the commands were actually executed and their results inspected.

---

## Coding-Agent Workflow

For every development task:

### 1. Understand

- Read this file and `docs/BUILD_STATUS.md`.
- Read the relevant spec/config/test/code files.
- Identify whether the requested capability is implemented, planned, or a contract change.

### 2. Define behavior

- State the expected input, output, failure cases, and acceptance test.
- Reuse existing schemas/configuration where possible.
- Ask only when an unresolved choice materially changes product behavior, security, or evaluation validity.

### 3. Implement minimally

- Make the smallest coherent change that completes one milestone or vertical slice.
- Keep deterministic logic independent from Streamlit and the LLM.
- Avoid unrelated refactors and speculative infrastructure.

### 4. Validate

- Add/update tests before marking work complete.
- Run relevant tests, configuration validation, and compilation.
- Inspect generated data/results manually against the canonical scenarios when applicable.
- Test failure and abstention paths, not only the happy path.

### 5. Review

- Check data leakage, double-counting, time-window correctness, security, redaction, evidence traceability, uncertainty language, and unintended changes.
- Inspect the diff before reporting completion.

### 6. Report

Report:

1. what changed;
2. why it changed;
3. tests/checks actually run;
4. limitations or assumptions;
5. the next logical milestone.

The user prefers explanations from basic to advanced. Explain the business purpose of a module before discussing its technical implementation.

---

## Definition of Done

A feature is done only when:

- its expected behavior is written or mapped to an existing specification;
- inputs/outputs and failure behavior are explicit;
- code follows the repository boundaries;
- deterministic calculations are independently testable;
- relevant tests are added or updated and actually run;
- evidence, uncertainty, privacy, and authorization are considered;
- documentation/configuration is updated when a contract changes;
- no unrelated behavior was silently altered;
- demo-visible claims are generated from data rather than manually typed;
- `docs/BUILD_STATUS.md` reflects reality.

---

## Scope Control

Do not add these during the initial hackathon prototype unless explicitly approved:

- FastAPI/microservices;
- React frontend;
- Kafka or live event streaming;
- production Fabric/Snowflake/Databricks integration;
- graph database or graph neural network;
- vector database or broad RAG system;
- complex causal inference;
- production identity provider;
- automatic account action or regulatory filing;
- real bank/customer data.

Production architecture may be documented separately, but the working prototype must remain reliable, explainable, testable, and finishable within the hackathon timeline.
