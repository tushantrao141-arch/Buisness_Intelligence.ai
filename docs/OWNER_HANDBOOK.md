# SilentSignal Owner Handbook

This is the material the product owner must understand and approve personally.
It separates external facts, project assumptions, calculated evidence, and
decisions requiring bank governance.

## Product problem

Banks already have threshold reports, KYC records, monitoring alerts and case
queues. The product problem is not the absence of data; it is the difficulty of
joining those fragments quickly enough to answer: **which movement or connected
pattern deserves human attention, why, how reliable is the explanation, and
what action is permitted?**

RBI's KYC direction requires regulated entities to monitor transactions and
describes ongoing due diligence as checking whether activity is consistent with
knowledge of the customer, the customer's business and risk profile. It also
calls out large or complex transactions, unusual patterns without apparent
economic rationale, threshold breaches, and turnover inconsistent with the
profile. RBI explicitly says AI/ML may support effective monitoring; it does
not delegate the regulated decision to an AI system. [RBI KYC Master Direction
(updated November 2024)](https://systemhealth.rbi.org.in/Scripts/BS_ViewMasDirections.aspx_id%3D11566%282%29.html)

SilentSignal therefore supports prioritisation and evidence review. It does not
determine criminality, file a report, freeze an account, or replace authorised
bank personnel.

## KPI meanings and approval questions

### Near-Threshold Value Ratio

Meaning: the percentage of relevant cash value inside the governed band below
an illustrative ₹10 lakh threshold. It identifies concentration near a boundary
but does not establish structuring or suspicion.

Faithful fact: the PML Rules cover cash transactions above ₹10 lakh and series
of integrally connected cash transactions individually below ₹10 lakh whose
monthly aggregate exceeds ₹10 lakh. They also cover suspicious transactions
whether or not made in cash. [FIU-India: PML Rules notification](https://fiuindia.gov.in/files/AML_Legislation/notification.html)

Owner approval: ₹10 lakh is connected to the reporting framework, but the
80%–100% proximity band is a transparent prototype policy choice. A bank would
need to validate and approve the band, scope, exclusions, and monitoring grain.

### Linked-Pattern Exposure

Meaning: unique transaction value belonging to connected clusters that pass
transparent review rules. It prevents duplicate counting and measures exposure,
not guilt.

Owner approval: approve the relationship types, qualifying score, review
window, and whether aggregate value is the right prioritisation measure.

### High-Risk Cluster Count

Meaning: the number of distinct clusters above an internal review-score
threshold. The score is a deterministic queue-prioritisation score—not a
probability that money laundering occurred.

Owner approval: approve every score component and the threshold of 60; demand
back-testing before production.

### Alert Investigation Yield

Meaning: positive completed investigations divided by all completed
investigations. Open cases are excluded to avoid label leakage.

Owner approval: define what counts as a positive disposition, monitor label
delay, and never optimise yield alone because it can encourage under-reporting.

### Case SLA Risk

Meaning: active cases due within 24 hours. It is an operational-capacity KPI,
not an AML-risk score.

Owner approval: approve the horizon, eligible statuses, holiday/calendar rules,
and ownership model.

The exact formulas and ten-row arithmetic are in `KPI_MANUAL_VERIFICATION.md`.

## Scenario ground truth

- **S1 strong connected pattern — ALERT.** Eight new WEST accounts repeatedly
  transact below the illustrative threshold, across branches, with shared
  fabricated identifiers and beneficiary. Expected explanation: new-account
  cohort, connected branches and relationship cluster.
- **S2 seasonal activity — MONITOR.** A mature cash-intensive EAST business has
  fresh KYC, activity within its documented turnover, and no material connected
  cluster. Seasonal activity is a supported alternative, not a conclusion.
- **S3 insufficient evidence — ABSTAIN.** NORTH activity is relevant, but KYC is
  stale and entity mapping is incomplete. The correct action is to request data,
  not escalate automatically.
- **S4 sparse channel — PEER_BASED.** SOUTH `NEW_DEPOSIT` has only fourteen days
  of history. The system uses comparable peers, caps confidence, and labels the
  method.
- **S5 unauthorised access — ACCESS_DENIED.** A WEST investigator requesting
  NORTH detail is rejected before evidence construction.

Ground truth is created before analytics and stored separately. Only evaluation
code reads it. Product owners should inspect the generator and approve whether
the scenarios are realistic enough for a demonstration; they are not a claim of
real-world prevalence.

## Business rules requiring approval

- ₹1,000,000 illustrative threshold and 0.80 proximity lower bound.
- 28-day baseline and seven-day current window.
- Relationship eligibility: shared fabricated phone, address or beneficiary;
  groups larger than ten are excluded from direct pairwise linking.
- Review score components and qualifying threshold of 60.
- KYC freshness SLA of 30 hours in the demo. This is a deliberately strict
  evidence-quality setting, not RBI's periodic KYC-update schedule.
- Evidence-confidence abstention below 0.60.
- Sparse-history definition below 28 days and peer-based confidence cap.
- Role-region matrix and identifier masking.
- Illustrative false-positive review cost of ₹250,000 used only for method
  comparison.

Important nuance: RBI's June 2025 amendment says low-risk individual customers
whose periodic KYC update is due should continue to be allowed transactions
while KYC is updated within the specified window and remain under regular
monitoring. SilentSignal therefore uses stale KYC to **reduce explanation
confidence and block unsupported escalation**, not to block the customer's
transactions. [RBI KYC Amendment Directions, 2025](https://www.rbi.org.in/scripts/NotificationUser.aspx/searchnew/searchnew/NotificationUser.aspx?Id=12866)

## Do the explanations make sense?

Approve an explanation only when:

1. The KPI definition, actual, expected and change match deterministic outputs.
2. Mutually exclusive driver leaves sum to the total movement; unexplained is zero.
3. Supporting, contradicting and alternative evidence are shown together.
4. Confidence reflects freshness, mapping completeness, sample size, source
   quality and historical coverage separately from pattern strength.
5. Every numeric narrative value is copied from the structured evidence packet.
6. The wording says “review signal” or “pattern,” never “criminal,” “fraud,” or
   “money laundering proven.”

## Are the actions appropriate?

- **Consolidate linked events:** appropriate for an entitled investigator when
  a connected pattern is supported; preserves relationships without deciding disposition.
- **Request KYC refresh:** appropriate under low confidence; gathers evidence
  and does not restrict the customer.
- **Monitor seasonal activity:** appropriate when current profile data supports
  a legitimate alternative; creates a time-bound check.
- **Reallocate investigation capacity:** appropriate for the Compliance Head
  when SLA exposure rises; acts on operations rather than the customer.

Not implemented by design: automatic STR filing, customer accusation, account
freeze, transaction blocking, regulatory conclusion, or autonomous case closure.

## Why each method was selected

- **Deterministic KPI functions:** exact, unit-testable arithmetic; prevents an
  LLM from inventing quantitative truth.
- **28-day governed baseline:** enough demo history for four weekly cycles while
  remaining inspectable; not a production seasonality model.
- **Business materiality plus z-score:** avoids ranking statistically unusual
  but immaterial noise alone.
- **Transparent NetworkX graph:** judges and investigators can inspect nodes,
  edges and score components; a GNN would add opacity without justified data.
- **Mutually exclusive leaf decomposition:** contributions reconcile exactly,
  unlike summing separate marginal views that double-count transactions.
- **Evidence confidence separate from pattern strength:** a strong-looking
  pattern can still be unsupported when KYC or mapping is stale.
- **Abstention:** prevents high-impact recommendations when critical evidence is
  missing.
- **Peer comparison for sparse history:** avoids pretending that fourteen days
  constitute a stable long-history baseline.
- **Evidence-packet-only narrative:** keeps quantitative truth and entitlements
  outside the language model; deterministic fallback keeps the demo available.

## What you should say to judges

“SilentSignal is a synthetic decision-support prototype. The ₹10 lakh reference
is grounded in India's cash-reporting framework, but our 80% proximity band,
review score and confidence weights are governed demonstration choices. The
system prioritises review, shows alternatives and abstains when evidence is
weak. It never proves wrongdoing or automates a regulatory action.”

