# Milestone Build and Failure Playbook

Every milestone states what exists, why it exists, where it lives, how to prove
it, the expected result, and common failure cases. Do not advance a production
version unless the owner understands the current module.

## 1. Product contract

- **Build:** user, data, KPI, scenario, action, security and non-goal specs.
- **Why:** the correct behavior must be defined before code.
- **Files:** `docs/PRODUCT_SPEC.md`, `DATA_SPEC.md`, `KPI_SPEC.md`,
  `EXPECTED_RESULTS.md`, `REQUIREMENTS_MATRIX.md`.
- **Proof:** explain the product without naming Python, Streamlit or NetworkX.
- **Expected:** two roles, three sources, five KPIs and five acceptance scenarios.
- **Failures:** technology-first description; missing non-goals; scenario labels
  invented after seeing output.

## 2. Reproducible skeleton

- **Build:** fixed dependencies, six Streamlit surfaces, launch/test scripts.
- **Why:** judges need a clean, repeatable run.
- **Files:** `requirements.txt`, `app.py`, `pages/`, `run_app.ps1`, `run_tests.ps1`.
- **Run:** `.\run_app.ps1`.
- **Expected:** every surface opens without exception.
- **Tests:** `tests/test_pages.py`.
- **Failures:** Python unavailable; blocked package download; port already used;
  running outside the project directory.

## 3. Synthetic sources and ground truth

- **Build:** transactions, KYC, cases, source metadata and isolated labels.
- **Why:** correct expected behavior must predate analytics.
- **Files:** `src/data_generator.py`, `data/raw/`, `data/ground_truth/`.
- **Run:** `.venv\Scripts\python.exe scripts\generate_demo.py`.
- **Expected:** 8,085 transactions, 339 KYC rows, 124 case events and S1–S5.
- **Failures:** non-deterministic seed; timestamps after as-of; ground truth read
  by analytics; accidental real identifiers.

## 4. Five KPIs

- **Build:** pure formulas, ten-row hand examples, unit tests, UI values.
- **Why:** quantitative truth must be inspectable and LLM-independent.
- **Files:** `src/kpis.py`, `docs/KPI_MANUAL_VERIFICATION.md`,
  `tests/test_kpi_examples.py`, `pages/1_KPI_Pulse.py`.
- **Expected:** all manual answers match code exactly.
- **Failures:** wrong denominator; duplicate linked transaction; open case in
  yield; overdue case confused with due-to-breach case.

## 5. Vertical slice

- **Build:** data → KPI → movement → explanation → permitted action.
- **Why:** proves the layers connect before breadth is added.
- **Files:** `src/runtime.py`, `app.py`, pages 1–4.
- **Expected:** S1 flows end to end.
- **Failures:** independent page mocks; values typed into UI; action not linked
  to evidence.

## 6. Movement and priority

- **Build:** current, expected, delta, z-score, impact, materiality and priority.
- **Why:** unusualness alone is not business importance.
- **Files:** `src/analytics.py`, page 1.
- **Expected:** WEST connected movement ranks above normal variation.
- **Failures:** zero-variance baseline; divide by zero; sparse channel treated as
  stable history; statistical score shown as probability.

## 7. SilentSignal relationships

- **Build:** customer, account, transaction, beneficiary, branch and shared-ID
  relationships plus account-level connected components.
- **Why:** repeated below-threshold events become meaningful together.
- **Files:** `src/analytics.py`, page 3.
- **Expected:** S1 forms a connected cross-branch new-account cluster.
- **Failures:** duplicate transaction exposure; high-degree common identifier
  creates a super-node; raw identifiers shown; risk score described as guilt.

## 8. Reconciled drivers

- **Build:** mutually exclusive leaf decomposition and waterfall.
- **Why:** separate marginal views double-count; judge proof must reconcile.
- **Files:** `src/analytics.py`, page 2, `tests/test_analytics.py`.
- **Expected:** sum(contributions) = KPI movement; unexplained = 0.
- **Failures:** mixing percent and INR; absent zero-days; summing the same
  transaction once per dimension.

## 9. Evidence confidence and abstention

- **Build:** freshness, mapping, sample, history, pattern and source gates.
- **Why:** pattern strength and evidence quality are different questions.
- **Files:** `src/data.py`, `src/analytics.py`.
- **Expected:** S1 supported; S3 abstains; S4 peer-based and capped.
- **Failures:** stale KYC automatically blocks customer transactions; confidence
  presented as probability; alternative hypothesis omitted.

## 10. Structured evidence packet

- **Build:** one masked, access-checked record for every narrative claim.
- **Why:** prevents unrestricted rows or invented numbers reaching an LLM.
- **Files:** `src/evidence.py`, `tests/test_evidence.py`, page 3.
- **Expected:** packet has KPI, drivers, reconciliation, freshness, missing data,
  method, confidence, alternatives, evidence IDs and actions.
- **Failures:** filtering after packet construction; raw account ID in JSON;
  narrative pulls directly from DataFrames.

## 11. Persona narratives

- **Build:** management and investigator wording from the packet only, plus fallback.
- **Why:** roles need different decisions from the same verified evidence.
- **Files:** `src/narrative.py`, page 3.
- **Expected:** different narrative, identical quantitative truth; app works offline.
- **Failures:** LLM calculates values; missing evidence citation; deterministic
  fallback drifts from packet.

## 12. Security

- **Build:** region entitlement, detail permission and masking before evidence.
- **Why:** restricted data must not enter prompts or UI components.
- **Files:** `src/security.py`, `src/evidence.py`, security tests, page 5.
- **Expected:** WEST → NORTH detail returns ACCESS_DENIED first.
- **Failures:** filter after join; aggregate persona receives entity list; security
  denial not audited.

## 13. Actions, feedback and telemetry

- **Build:** accept/reject actions; explanation correctness; corrected driver;
  role; latency; LLM calls/tokens/cost/cache; persistence.
- **Why:** learning and operational accountability require durable outcomes.
- **Files:** `src/storage.py`, pages 4–5.
- **Expected:** SQLite events remain after restart.
- **Failures:** schema migration omitted; free-text only; user role missing;
  demo telemetry manually typed.

## 14. Comparative evaluation

- **Build:** threshold, movement, proximity and full-method comparison.
- **Why:** differentiation must be measured, not asserted.
- **Files:** `src/evaluation.py`, `docs/EVALUATION_REPORT.md`, page 5.
- **Expected:** automatic precision, recall, F1, cost, missed patterns, driver,
  abstention, narrative, latency and cost results.
- **Failures:** ground truth used during detection; tiny synthetic result presented
  as production accuracy; false-positive cost not labelled as an assumption.

## 15. Submission and deployment

- **Build:** README, deck, five-minute script, deployment instructions, clean ZIP.
- **Why:** judging evaluates visible proof and delivery, not repository depth alone.
- **Files:** `README.md`, `docs/DEMO_SCRIPT.md`, `docs/DEPLOYMENT.md`, judge deck.
- **Expected:** local and packaged versions pass the same tests.
- **Failures:** public deployment exposes secrets; video depends on network;
  demo exceeds five minutes; screenshots show contradictory numbers.

