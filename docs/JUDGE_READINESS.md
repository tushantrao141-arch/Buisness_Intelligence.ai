# SilentSignal Judge Readiness Audit

Audit date: 24 August 2026

## Bottom line

SilentSignal is a complete, locally verified judge prototype. The product,
analytics, graph context, explanations, security boundaries, actions, feedback,
evaluation, documentation, screenshots, and judge deck are implemented.

Three submission steps still require the human owner or an external account:

1. Publish the repository through the owner's GitHub and Streamlit Community
   Cloud accounts.
2. Validate the public URL on a physical second device. A 390×844 responsive
   browser emulation already passes, but that is not a physical-device test.
3. Record human narration and rehearse the five-minute demonstration under the
   actual event rules. A timed script and visual backup are supplied.

The original milestone asked for an initial skeleton commit. The repository was
initialized after the application already existed, so a historical skeleton
commit cannot be recreated faithfully. The final verified source is committed.

## Requirement audit

### Product and specifications — complete

- Two operational users are explicit: Compliance Head and Regional Investigator.
- Three heterogeneous sources are generated: transactions, KYC/customer records,
  and investigation case events.
- Five governed KPIs, four analytical scenarios, a separate access-control
  scenario, permitted actions, security rules, and exclusions are documented.
- Product, data, KPI, expected-results, and requirements specifications exist.
- The product can be explained without referring to the technology stack.

### Reproducible project and data — complete

- The requested application structure exists.
- Dependencies are pinned to exact installed versions.
- One command regenerates deterministic synthetic data and ground truth.
- Strong connected activity, legitimate seasonality, stale/missing evidence, and
  sparse new-channel history are injected and automatically checked.
- Git is initialized and the final verified snapshot is committed.

### KPI calculations — complete

For all five KPIs the repository contains the exact formula, a hand-worked
10-row example, the expected answer, pure implementation, test, and Streamlit
display. The LLM is not used for any KPI calculation.

### End-to-end movement and graph differentiation — complete

- Baseline, actual, difference, unusualness, impact, priority score, and rank are
  calculated.
- The threshold-only baseline misses the injected connected pattern while the
  full method finds it.
- The heterogeneous graph contains customer, account, transaction, beneficiary,
  branch, and shared-identifier nodes.
- The strong scenario produces an evidence-supported result; stale evidence
  produces abstention; sparse history uses a peer comparison.

### Drivers and evidence — complete

- Region, branch, channel, account age, customer category, and connected cluster
  are represented as mutually exclusive leaf drivers.
- Ranked driver contributions reconcile exactly to total KPI movement; the UI
  displays contribution percentages, waterfall, explained, and unexplained totals.
- Every explanation is rendered from one structured evidence packet containing
  the KPI contract and values, drivers, reconciliation, freshness, missing data,
  method, confidence, alternatives, evidence IDs, and permitted actions.
- Access enforcement is the first executable packet step. The optional LLM path
  receives the sanitized packet only; deterministic narratives work without it.

### Security, actions, feedback, and telemetry — complete

- Compliance Head sees aggregate all-region information; regional investigators
  are region-scoped and blocked from other-region evidence.
- Sensitive identifiers are masked and tests prove unauthorised evidence cannot
  enter a packet.
- Actions are bounded to review, monitor, request evidence, or escalate; there is
  no automatic account freeze, customer block, or regulatory filing.
- Correctness, corrected driver, accept/reject decision, user role, latency, LLM
  calls, tokens, estimated cost, and cache status are persisted or reported.

### Evaluation — complete for prototype acceptance, not production validation

Automatic evaluation reads the isolated ground-truth file and compares four
methods. The latest deterministic run produced:

- 5 of 5 scenario/control outcomes passed.
- Threshold only: F1 0.000; connected pattern missed.
- Movement detector: F1 0.667; one illustrative false positive.
- Movement + proximity: F1 0.667; one illustrative false positive.
- Full SilentSignal: precision 1.000, recall 1.000, F1 1.000, driver ranking
  accuracy 1.000, abstention correctness 1.000, and narrative numerical accuracy
  1.000.
- Zero LLM calls and zero measured model cost.

These are results on a very small synthetic acceptance set. They demonstrate
correct implementation against designed ground truth; they are not estimates of
real-world AML performance. The ₹250,000 false-positive handling cost is an
explicit illustrative assumption, not measured bank cost.

## Owner facts and approvals

### Product problem

The problem is not merely finding large transactions. It is deciding whether a
material KPI movement is operationally meaningful, what evidence explains it,
how uncertain that explanation is, and what a permitted reviewer should do next.
RBI's KYC direction supports ongoing monitoring consistent with the customer's
business, risk profile, and unusual transaction patterns. SilentSignal is a
decision-support prototype for that operating need; it does not determine guilt.

### KPI meanings

- Near-threshold value ratio measures concentration in a governed proximity band.
  The 80–100% band is a prototype rule. It is not itself a statutory definition
  of evasion or suspicious behaviour.
- Linked-pattern exposure measures unique transaction value attached to qualifying
  graph patterns, with transactions counted once.
- High-risk cluster count is a prioritisation queue count, not a count of customers
  proven suspicious.
- Alert investigation yield is an operational effectiveness ratio and changes
  when the institution's closure policy changes.
- Case SLA risk measures workflow/control pressure, not financial-crime probability.

FIU's published PML Rules material describes cash reporting above ₹10 lakh and
integrally connected monthly series above ₹10 lakh, while suspicious transaction
reporting is a separate obligation whether or not the transaction is cash. The
project uses ₹10 lakh only as a reporting reference and keeps the proximity band
under explicit prototype governance.

### Scenario ground truth

- S1 strong connected pattern: expected ALERT.
- S2 legitimate seasonal activity: expected MONITOR.
- S3 insufficient evidence: expected ABSTAIN.
- S4 sparse-history channel: expected PEER_BASED.
- S5 unauthorised region: expected ACCESS_DENIED before evidence retrieval.

Ground truth is isolated from analytics and is read only by the evaluation code.

### Business rules

- A score prioritises review; it is not a calibrated probability or proof.
- Confidence combines data sufficiency and support; low confidence abstains.
- Stale KYC reduces confidence but does not automatically block transactions.
- Role and region checks precede entity access.
- Aggregate explanations do not expose raw entity lists.
- Every action remains human-reviewed and auditable.

### Explanation approval

An explanation is acceptable only when every number is copied from the evidence
packet, its driver contributions reconcile, the evidence IDs are available, the
confidence and alternative hypothesis are visible, and the language does not turn
a review signal into a conclusion of wrongdoing.

### Action approval

Appropriate prototype actions are to review, monitor, request missing evidence,
or escalate within the case workflow. Automatic freeze, customer blocking, and
automatic STR filing are deliberately excluded because those actions require
institution-specific legal, policy, and human decision processes.

### Why the methods were selected

- Deterministic formulas make KPI values reproducible and auditable.
- Historical baselines expose change, while business impact prevents a statistical
  oddity from dominating the queue.
- Proximity logic adds governed context but cannot see coordinated networks alone.
- Heterogeneous graph analysis represents relationships that row-wise thresholds miss.
- Mutually exclusive driver leaves make the movement arithmetic provable.
- Separate pattern strength and evidence confidence prevent a strong-looking pattern
  from hiding weak or stale data.
- Structured evidence packets enforce traceability and a safe LLM boundary.
- Deterministic fallback keeps the system demonstrable and testable without an API.
- Baseline comparison proves incremental value instead of evaluating only the final method.

## Calibrated selection estimate

There is no faithful exact probability without the competition name, rubric,
number of submissions, shortlist size, and judge preferences. A reasonable
heuristic based only on the artefacts is:

- Prototype/evidence readiness: approximately 86 out of 100.
- Selection chance if judges prioritise technical completeness, explainability,
  safety, and a strong live demo: roughly 55–75%.
- Selection chance if the round expects a public deployment, real labelled data,
  institutional integration, or demonstrated traction: roughly 35–55% today.
- After public deployment, physical-device validation, a rehearsed narrated demo,
  and clear event-specific framing: roughly 65–80% for a prototype-oriented round.

These ranges are judgement calls, not statistical forecasts. The most important
remaining risk is not missing code; it is overclaiming synthetic results or
arriving without a reliable public demo.

## Primary factual sources

- Reserve Bank of India, Master Direction — Know Your Customer Direction, 2016
  (updated 6 November 2024):
  https://systemhealth.rbi.org.in/Scripts/BS_ViewMasDirections.aspx_id%3D11566%282%29.html
- Financial Intelligence Unit — India, PML Rules notifications and reporting
  thresholds: https://fiuindia.gov.in/files/AML_Legislation/notification.html
- Reserve Bank of India, KYC Amendment Directions, 2025:
  https://www.rbi.org.in/scripts/NotificationUser.aspx/searchnew/searchnew/NotificationUser.aspx?Id=12866
