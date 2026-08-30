# BusinessIntelligence.ai - SilentSignal

## Judge submission README

**SilentSignal is an evidence-first KPI intelligence-to-action workspace for banking risk operations.** It helps a compliance team decide which KPI movement or connected activity pattern deserves attention, why it became material, how trustworthy the explanation is, and what the current user is permitted to do next.

This is a complete synthetic prototype built for the Accenture BusinessIntelligence.ai innovation challenge. It does not use real customer data, does not determine criminality, and does not require an LLM to calculate or explain its quantitative results.

**Repository:** [github.com/tushantrao141-arch/Buisness_Intelligence.ai](https://github.com/tushantrao141-arch/Buisness_Intelligence.ai)

> The central design idea is simple: a risk signal is useful only when the reviewer can trace it from source freshness, through deterministic calculation and driver contribution, to evidence confidence and a governed human action.

## 1. Executive summary

Banking teams often have transaction monitoring, KYC records, case queues, and dashboards, but these systems leave an important decision fragmented. A dashboard may show that a KPI changed without explaining which connected activity drove it, whether the evidence is fresh enough to trust, or what action is allowed for the current reviewer.

SilentSignal joins those decisions into one workflow:

1. Reconcile three synthetic sources with different grains and refresh cadences.
2. Calculate five governed KPIs using deterministic, unit-tested formulas.
3. Detect statistically unusual and operationally material KPI movement.
4. Build transparent relationships across accounts, identifiers, beneficiaries, branches, and transactions.
5. Reconcile ranked driver contributions back to the KPI delta.
6. Separate pattern strength from evidence confidence.
7. Alert when evidence is strong, present alternatives when activity may be legitimate, and abstain when evidence is weak.
8. Enforce persona and region entitlements before restricted evidence is built.
9. Recommend only actions defined in a governed playbook.
10. Record runtime, feedback, actions, and security events for audit.

The application is designed as a decision-support workspace, not as an autonomous compliance judge. Every material conclusion remains reviewable by a human.

## 2. What judges should notice

- **Connected intelligence, not an isolated dashboard:** five KPIs form one operational journey from activity concentration to connected exposure, investigation priority, effectiveness, and case capacity.
- **Evidence before narrative:** every value, driver, confidence result, and action comes from deterministic services and a validated evidence packet.
- **Honest uncertainty:** the prototype supports ALERT, MONITOR, ABSTAIN, PEER_BASED, and ACCESS_DENIED outcomes instead of forcing every signal into an escalation.
- **Transparent differentiation:** a threshold-only method misses the designed connected pattern, while the full method finds it and correctly abstains when evidence quality is poor.
- **Security by execution order:** region authorization is checked before restricted evidence construction or any optional LLM invocation.
- **LLM-safe architecture:** the LLM is optional and disabled in the verified run. It may phrase a validated packet, but it may not calculate KPIs, scores, contributions, confidence, or actions.
- **Reproducible proof:** fixed-seed synthetic data, isolated ground truth, governed YAML, hand-verifiable KPI examples, scenario tests, page smoke tests, and runtime telemetry support every demo claim.

## 3. Minimum prototype expectations - coverage

| Expected capability | SilentSignal implementation | Judge proof |
|---|---|---|
| Three to five connected KPIs | Five governed KPIs and an operational relationship map | Command Center and KPI Pulse |
| Two or three sources with different grains and cadences | Transactions, KYC, and cases | Source readiness and Governance |
| Lightweight semantic contract | YAML definitions, formulas, drivers, materiality, lineage, history, and access | KPI Pulse contract drawer |
| Two personas with different narratives and actions | Compliance Head and Regional AML Investigator | Persona selector and Actions |
| Multi-factor KPI movement | Region, branch, channel, account age, and relationship contributions | Why It Changed waterfall |
| Low-confidence scenario | Stale KYC and incomplete mapping produce ABSTAIN | NORTH investigation |
| Sparse-history scenario | Fourteen-day NEW_DEPOSIT channel uses a peer baseline | SOUTH KPI view |
| Role-based security | WEST investigator is denied NORTH detail before packet creation | Governance security tab |
| Freshness, method, contribution, confidence, and lineage | Structured evidence packet and visible proof panels | Investigation and Governance |
| LLM versus non-LLM breakdown | Human-readable execution boundary and zero-call run | Governance runtime tab |
| Runtime telemetry | Latency, calls, tokens, cost, and cache | Governance runtime tab |

## 4. Users and the decision they need to make

### Compliance Head

The Compliance Head needs an aggregate view of exposure, regional contribution, investigation capacity, SLA pressure, confidence, and evidence gaps. This persona may review all configured regions, but receives aggregate or masked entity information by default. Typical actions include reallocating investigation capacity or requesting improved evidence.

### Regional AML Investigator

The investigator needs detail only for the assigned region: masked entities, linked transactions, branch and timing patterns, alternative explanations, missing evidence, and case-level next steps. Typical actions include consolidating linked events, requesting KYC refresh, or monitoring a documented seasonal profile.

### Primary decision

> Which KPI movement or connected activity pattern should be investigated first, why did it become material, how trustworthy is that explanation, and what is the next permitted action for this user?

## 5. Governed data foundation

All prototype data is synthetic, deterministic, and generated with seed 42. Timestamps are stored in UTC and currency values use INR. The analytical as-of snapshot contains 90 days of history.

| Source | Grain | Simulated cadence | Current synthetic rows | Purpose |
|---|---|---:|---:|---|
| `transactions.csv` | One row per transaction event | 15 minutes | 16,917 | Amount, time, branch, channel, region, type, beneficiary relationship |
| `kyc.csv` | One row per account snapshot | Daily | 339 | Business profile, risk tier, account age, expected turnover, shared identifiers, KYC freshness |
| `cases.csv` | One row per case-status event | 4 hours | 124 | Case state, ownership, region, SLA due time, and final disposition |

`source_metadata.json` records generation time, last refresh, freshness SLA, row count, and schema version. Data-quality checks reject duplicate transaction IDs and non-positive amounts, quarantine unknown regions, retain unmatched accounts with explicit flags, detect future timestamps, and preserve original transaction IDs through transformation.

Ground truth is stored separately in `data/ground_truth/events.csv`. It is never read by KPI, graph, driver, confidence, narrative, or action modules. Only the held-out evaluation code may read it after analytics finish.

## 6. Five connected KPI contracts

The machine-readable source of truth is `configs/kpi_contracts.yaml`. Each contract contains its business definition, exact calculation, unit, grain, owner, sources, drivers, calculation constraints, freshness SLA, minimum history, materiality gate, access policy, and transformation lineage.

| KPI | Business question | Deterministic formula | Grain |
|---|---|---|---|
| Near-Threshold Value Ratio | How concentrated is relevant cash activity inside the governed proximity band? | Qualifying near-threshold cash value / all relevant cash value in the same slice x 100 | Region-day |
| Linked-Pattern Exposure | What unique value belongs to qualifying connected clusters? | Sum unique transaction value in qualifying clusters; never count a transaction twice | Region-day |
| High-Risk Cluster Count | How many connected clusters pass the transparent review gates? | Count distinct qualifying cluster IDs | Region-day |
| Alert Investigation Yield | Of completed investigations, how many were confirmed or escalated? | Positive completed cases / all completed investigated cases x 100 | Region-week |
| Case SLA Risk | How many active cases are due within the governed horizon? | Count open or in-review cases due within 24 hours | Region-hour |

### Materiality policy

- Percentage KPIs require an absolute movement of at least 5 percentage points **and** an absolute z-score of at least 1.5.
- Linked-Pattern Exposure requires an increase greater than INR 50 lakh **and** a z-score of at least 1.5.
- Count KPIs require an increase of at least 2 **or** a z-score of at least 2.

### Connected-pattern qualification

A relationship component qualifies for the review queue only when all three configured gates pass:

- review score is at least 60;
- at least 4 recent near-threshold events exist; and
- at least 50% of connected accounts contribute recent near-threshold activity.

The coverage gate prevents a small number of transactions inside a broad, diffuse component from being presented as a focused pattern. The review score is a queue-prioritization score, not a probability of wrongdoing.

### Why the KPIs are connected

```text
Near-Threshold Value Ratio
        -> Linked-Pattern Exposure
        -> High-Risk Cluster Count
        -> Alert Investigation Yield
        -> Case SLA Risk
```

The connection is operational, not causal. Concentrated activity can create connected exposure; qualifying clusters enter the review queue; investigation outcomes measure effectiveness; and case SLA risk reveals whether the operation has enough capacity to respond.

## 7. End-to-end analytical workflow

```text
Synthetic source events
        -> validation, reconciliation, and freshness
        -> derived deterministic features
        -> KPI calculation and historical baseline
        -> statistical and business materiality
        -> transparent relationship graph
        -> mutually exclusive driver contribution
        -> evidence confidence and abstention gate
        -> authorization and identifier masking
        -> validated evidence packet
        -> deterministic or optional LLM narrative
        -> governed action and audit telemetry
```

### Movement detection

For each KPI and region, the engine compares the current value with a governed 28-day historical mean and standard deviation. It calculates actual, expected, delta, percentage change, z-score, business impact, materiality, and priority. Materiality thresholds come from configuration instead of page code or hidden constants.

### Relationship analysis

NetworkX builds a transparent heterogeneous graph from shared fabricated phones, addresses, beneficiaries, branches, accounts, customers, and transactions. Connected components receive deterministic review features such as account count, near-threshold activity, active-account coverage, branch spread, relationship types, exposure, and review score.

### Driver contribution

The engine decomposes KPI movement into mutually exclusive leaf segments across region, branch, channel, account age, customer profile, and connected cluster. The ranked contributions add back to the observed KPI movement, with any unexplained residual shown explicitly. Associations are described as explanatory contribution, not as causation.

### Confidence and abstention

Pattern strength and evidence confidence are deliberately separate. Confidence considers source freshness, KYC freshness, mapping completeness, historical coverage, sample sufficiency, and contradictory or alternative evidence. When the confidence gate fails, SilentSignal requests missing information and abstains from a high-impact recommendation.

## 8. Canonical demonstration scenarios

### S1 - Strong connected pattern - WEST - ALERT

Eight related new accounts conduct repeated near-threshold cash activity across four branches over fourteen days and share fabricated identifiers or beneficiaries. The expected result is one focused connected cluster, material KPI movement, reconciled multi-factor drivers, high evidence confidence, and persona-appropriate investigation actions.

### S2 - Legitimate seasonal activity - EAST - MONITOR

A mature cash-intensive business shows seasonal activity consistent with expected turnover, has fresh KYC, and has no material cross-account relationship. SilentSignal shows the legitimate alternative hypothesis and recommends monitoring rather than claiming wrongdoing.

### S3 - Insufficient evidence - NORTH - ABSTAIN

Near-threshold activity exists, but KYC is stale, entity mappings are incomplete, and a legitimate explanation remains plausible. Confidence falls below 0.60, the engine asks for refreshed KYC and mapping information, and it abstains from escalation.

### S4 - Sparse-history channel - SOUTH - PEER_BASED

`NEW_DEPOSIT` has only fourteen days of history. The engine avoids pretending that a normal long-history baseline exists, uses labelled peer comparison when suitable, caps confidence, and abstains if comparable peers are insufficient.

### S5 - Unauthorized region - ACCESS_DENIED

A WEST investigator requests NORTH-region detail. Authorization is denied before restricted evidence construction or optional LLM invocation, and a security event is recorded.

## 9. What the evidence packet proves

The structured evidence packet is the single source for user-facing explanations. It includes:

- KPI ID, business definition, formula, unit, grain, owner, minimum history, and access policy;
- actual, expected, delta, percentage change, z-score, materiality, and priority;
- ranked driver contributions and reconciliation totals;
- source refresh timestamps, ages, SLAs, and row counts;
- analytical method and traceable transformation lineage;
- evidence confidence, reason codes, and missing-data gaps;
- supporting evidence, contradicting evidence, and legitimate alternatives;
- evidence IDs and masked identifiers;
- actions permitted for the current persona.

An explanation is accepted only when its numbers match this packet, driver contributions reconcile, evidence references exist, access rules are satisfied, and the language stays within decision-support boundaries.

## 10. LLM versus non-LLM processing

| Processing stage | Owner | LLM allowed? |
|---|---|---|
| Data validation, quality, and freshness | Deterministic Python | No |
| KPI values, baselines, materiality, and priority | Deterministic Python | No |
| Relationship graph and review score | NetworkX plus deterministic rules | No |
| Driver contribution and reconciliation | Deterministic arithmetic | No |
| Evidence confidence and abstention | Governed deterministic gates | No |
| Authorization, redaction, and action selection | Deterministic security and playbook rules | No |
| Persona-specific phrasing of a validated packet | Deterministic Jinja2 fallback or optional structured LLM | Optional |

Required execution order:

```text
deterministic analytics
        -> validated evidence packet
        -> authorization and redaction
        -> structured narrative output
        -> numeric and evidence-claim validation
        -> user interface
```

The verified prototype runs with `llm.enabled: false`, sends no raw identifiers to an LLM, makes zero model calls, uses zero tokens, and reports zero estimated model cost. If enabled later, the LLM still cannot calculate KPIs, invent facts, choose unapproved actions, or make a compliance disposition.

## 11. Security, privacy, and responsible use

- The current persona selector simulates entitlements; it is not presented as production authentication.
- The Compliance Head has aggregate all-region access and no entity-detail permission.
- Regional investigators can access only configured regional detail.
- Authorization runs before restricted queries, evidence construction, or narrative generation.
- Account and customer identifiers are masked in the UI, logs, screenshots, and narrative payload.
- All data is synthetic and reproducible; no real PII or bank data is included.
- Near-threshold activity alone is never treated as proof of suspicious or illegal conduct.
- The illustrative INR 10 lakh reference and 80%-100% proximity band are governed prototype choices, not a complete statement of regulation.
- SilentSignal never freezes an account, blocks a customer, files a regulatory report, or closes a case automatically.

Preferred language is "risk signal," "elevated exposure," "qualifying review pattern," "explanatory association," and "requires review." Review score and evidence confidence are never labelled as probability of guilt.

## 12. Streamlit decision workspace

| Surface | Judge question answered |
|---|---|
| Command Center | What needs attention, how do the KPIs connect, and are the source feeds ready? |
| KPI Pulse | Which movements are material, and what does each governed KPI contract mean? |
| Why It Changed | Which drivers contributed, by how much, and does the arithmetic reconcile? |
| SilentSignal Investigation | What relationship pattern and evidence support the finding, and what alternatives or gaps remain? |
| Actions | What is the next governed action for this persona, who owns it, and how will impact be monitored? |
| Governance | Are data quality, security, evaluation, feedback, runtime, LLM boundaries, and costs inspectable? |

Persona and region context persist across pages through governed URL and session state, preventing confusing resets during a live demonstration.

## 13. Evaluation and verification evidence

### Scenario acceptance

All five predefined outcomes pass: S1 ALERT, S2 MONITOR, S3 ABSTAIN, S4 PEER_BASED, and S5 ACCESS_DENIED.

### Four-method comparison

Alert metrics are calculated over S1-S4, with ALERT as the positive class. The acceptance set is intentionally small and synthetic; it proves implemented behavior against designed ground truth, not real-world model accuracy.

| Method | Precision | Recall | F1 | False alerts | Missed patterns | S3 abstention |
|---|---:|---:|---:|---:|---:|---:|
| Threshold only | 0% | 0% | 0% | 0 | 1 | 0% |
| Movement detector | 50% | 100% | 66.7% | 1 | 0 | 0% |
| Movement plus proximity | 50% | 100% | 66.7% | 1 | 0 | 0% |
| Full SilentSignal | 100% | 100% | 100% | 0 | 0 | 100% |

Full SilentSignal also achieves 100% driver-ranking accuracy, abstention correctness, and narrative numerical accuracy on the designed acceptance fixtures. These are prototype acceptance results, not production generalization claims.

### Verified engineering checks

- 66 automated tests pass.
- Project configuration and cross-file contracts validate.
- All six Streamlit surfaces render through automated smoke tests.
- KPI formulas have hand-verifiable ten-row examples, including zero-denominator and unique-transaction behavior.
- Fixed seed 42 produces deterministic source hashes.
- Referential integrity, no-future-time, graph, contribution, evidence, security, storage, evaluation, and page behavior are tested.
- Desktop and responsive 390 x 844 browser emulation were completed; physical mobile-device testing remains an owner step.

## 14. Runtime telemetry, feedback, and audit

The Governance workspace exposes end-to-end latency, model-call count, token usage, estimated USD cost, and cache status. Runtime varies by machine and is displayed from the latest execution instead of being typed into the page.

SQLite records runtime, action, feedback, and security events locally. Feedback captures explanation correctness, corrected drivers, accept or reject decisions, persona, and timestamps. This supports a future review loop without allowing feedback to silently change governed calculations.

For a production deployment, the local SQLite store would be replaced with a governed durable multi-user store and enterprise identity controls.

## 15. Architecture and repository map

SilentSignal remains one modular Python and Streamlit application so the prototype is transparent, testable, and finishable.

```text
app.py                         Streamlit Command Center
pages/                         Five decision-workflow pages
configs/                       KPI, user, action, safety, and runtime contracts
src/data_generator.py          Deterministic synthetic data and scenarios
src/data_quality.py            Validation, reconciliation, and freshness
src/kpi_engine.py              Pure KPI calculations
src/movement.py                Baselines and configured materiality
src/graph_engine.py            Transparent NetworkX relationships
src/driver_analysis.py         Reconciled contribution analysis
src/confidence.py              Evidence quality and abstention
src/evidence.py                Authorized structured evidence packets
src/narrative.py               Evidence-linked deterministic/optional LLM narrative
src/actions.py                 Role-governed playbook recommendations
src/security.py                Region authorization and masking
src/storage.py                 SQLite audit and feedback persistence
src/evaluation.py              Isolated ground-truth acceptance evaluation
src/telemetry.py               Latency, calls, tokens, cost, and cache
tests/                         66 unit, contract, integration, security, and UI checks
docs/                          Product, data, KPI, scenario, demo, and deployment evidence
```

Core technologies: Python 3.11+, Streamlit, Pandas, NumPy, DuckDB, PyArrow, Plotly, NetworkX, scikit-learn, Pydantic, YAML, Jinja2, SQLite, and an optional OpenAI narrative provider.

## 16. Run the project

### Fastest Windows setup

```powershell
.\run_app.ps1
```

The script creates `.venv`, installs dependencies, regenerates synthetic data, initializes the database, and starts Streamlit. Open the local URL printed by Streamlit, normally `http://localhost:8501`.

### Manual local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\generate_demo.py
python scripts\init_database.py
python -m streamlit run app.py
```

### Docker

```bash
docker compose up --build -d
```

Open `http://localhost:8501`. The container runs as a non-root user and includes a Streamlit health check.

### Tests and evaluation

```powershell
.\run_tests.ps1
```

Or run the checks directly:

```powershell
python scripts\validate_project.py
python -W ignore::DeprecationWarning -m unittest discover -s tests -v
python -m compileall -q app.py pages src scripts tests
python scripts\evaluate_demo.py
```

## 17. Recommended five-minute judge walkthrough

1. **Command Center - 25 seconds:** state the decision problem, synthetic-data boundary, connected KPI map, and source readiness.
2. **KPI Pulse - 45 seconds:** use Compliance Head and WEST; show actual versus expected, materiality, priority, and the contract drawer.
3. **Why It Changed - 45 seconds:** select Linked-Pattern Exposure; show ranked contributions and the explained/unexplained reconciliation.
4. **Investigation - 55 seconds:** show the focused eight-account pattern, masked evidence, method, lineage, confidence, and alternative hypothesis.
5. **Abstention - 40 seconds:** switch to the NORTH investigator; show stale KYC and incomplete mapping leading to ABSTAIN and a request for evidence.
6. **Actions - 35 seconds:** compare the Compliance Head action with the investigator action and show the monitoring KPI.
7. **Governance - 45 seconds:** show access denial, four-method comparison, LLM/non-LLM boundary, and live runtime telemetry.
8. **Close - 10 seconds:** "SilentSignal turns governed KPI movement into traceable evidence, honest uncertainty, and authorized human action."

## 18. Limitations and production path

This is a strong prototype, not a production AML platform. Current limitations are explicit:

- all data and scenarios are synthetic;
- evaluation uses a small designed acceptance set;
- thresholds and confidence weights need institution-specific validation and back-testing;
- the persona selector is an entitlement simulation, not enterprise authentication;
- local SQLite is not a durable multi-user production store;
- no live core-banking, case-management, or streaming integration is implemented;
- no public deployment URL or physical-device test is claimed in this document;
- no autonomous account, customer, case, or regulatory action is implemented.

A production path would add institution-approved policy calibration, representative historical validation, time-based held-out evaluation, enterprise identity, governed source connectors, durable telemetry storage, monitoring, human review procedures, and formal model-risk and compliance approval.

## 19. Judge-ready conclusion

SilentSignal demonstrates the full prototype expectation as one coherent decision journey:

**three governed sources -> five connected KPIs -> transparent multi-factor movement -> evidence and confidence -> persona-specific narrative -> authorized action -> runtime and audit proof.**

Its differentiator is not another alert. It is the traceable connection between governed measurement, relationship evidence, uncertainty, security, and human action. The system remains useful when the LLM is off, refuses to overstate weak evidence, and makes every demo claim inspectable in code, configuration, tests, or the Governance workspace.

## 20. Supporting documents

- `docs/PRODUCT_SPEC.md` - product decision, users, scope, and success criteria.
- `docs/DATA_SPEC.md` - source schemas, grains, cadences, and quality rules.
- `docs/KPI_SPEC.md` - business meaning and formulas for all five KPIs.
- `docs/KPI_MANUAL_VERIFICATION.md` - hand-worked ten-row KPI examples.
- `docs/EXPECTED_RESULTS.md` - predefined S1-S5 outcomes.
- `docs/EVALUATION_REPORT.md` - automatic acceptance and method comparison.
- `docs/DEMO_SCRIPT.md` - timed five-minute judge walkthrough.
- `docs/DEPLOYMENT.md` and `docs/DOCKER.md` - deployment and container instructions.
- `docs/OWNER_HANDBOOK.md` - business assumptions and approval boundaries.

## 21. Regulatory framing references

SilentSignal is not legal advice and does not fabricate compliance obligations. The project uses these sources only to frame ongoing monitoring and the illustrative cash-reporting reference:

- [Reserve Bank of India - Master Direction - Know Your Customer Direction, 2016](https://systemhealth.rbi.org.in/Scripts/BS_ViewMasDirections.aspx_id%3D11566%282%29.html)
- [Financial Intelligence Unit - India - PML Rules notifications](https://fiuindia.gov.in/files/AML_Legislation/notification.html)
- [Reserve Bank of India - KYC Amendment Directions, 2025](https://www.rbi.org.in/scripts/NotificationUser.aspx/searchnew/searchnew/NotificationUser.aspx?Id=12866)
