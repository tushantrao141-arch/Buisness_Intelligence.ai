# Buisness_Intelligence.ai

## SilentSignal

KPI intelligence-to-action workspace for banking risk operations.

SilentSignal watches governed KPIs, explains why they moved, connects related activity, and recommends only the next action the current user is allowed to take. It is a fully synthetic demo: no real customer data, and no LLM is required for the numbers.

**GitHub:** [tushantrao141-arch/Buisness_Intelligence.ai](https://github.com/tushantrao141-arch/Buisness_Intelligence.ai)

## What it does

1. Reconciles three sources: transactions, KYC, and investigation cases.
2. Calculates five governed KPIs against a 28-day baseline.
3. Builds a relationship graph (accounts, beneficiaries, branches, shared identifiers).
4. Ranks drivers so contributions add back to the KPI movement.
5. Separates pattern strength from evidence confidence, and abstains when quality is too low.
6. Shows Compliance Head vs regional investigator views, with region access checks.
7. Records actions, feedback, and security denials in a local SQLite audit store.

A review score is a signal for a human, not proof of wrongdoing. The app never takes a high-impact action on its own.

## Pages

| Page | Purpose |
|---|---|
| Command Center (`app.py`) | What needs attention in the selected region |
| KPI Pulse | Material movements and trend vs baseline |
| Why It Changed | Ranked drivers and residual |
| SilentSignal Investigation | Linked pattern, evidence, alternatives |
| Actions | Persona-permitted playbook steps |
| Governance | Quality, evaluation, security, runtime |

## Run locally (Windows)

```powershell
.\run_app.ps1
```

That creates `.venv`, installs `requirements.txt`, regenerates demo data, and starts Streamlit.

Manual setup:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/generate_demo.py
python scripts/init_database.py
streamlit run app.py
```

Open the local URL Streamlit prints. First load takes about 10 seconds while analytics run.

Suggested walkthrough: **Compliance Head** in **WEST**, then **North Regional AML Investigator** to see abstention.

## Tests

```powershell
.\run_tests.ps1
```

Or:

```powershell
python -m unittest discover -s tests -v
```

## Layout

```text
app.py                 Streamlit entry
pages/                 Five workflow pages
src/                   Analytics, security, evidence, storage
configs/               KPI contracts, users, action playbooks
data/raw/              Generated synthetic sources
data/ground_truth/     Evaluation labels only (not used in scoring)
scripts/               Generate data, evaluate, validate
tests/                 Unit and scenario tests
docs/                  Specs, demo script, evaluation notes
```

Pipeline:

```text
synthetic sources
  → quality + freshness
  → KPIs + movement
  → graph + drivers
  → confidence + abstention
  → persona narrative + governed action
  → audit + held-out evaluation
```

Ground truth is read only by `src/evaluation.py` after analytics finish.

## Docs

- [Owner handbook](docs/OWNER_HANDBOOK.md)
- [KPI formulas](docs/KPI_SPEC.md)
- [Demo script](docs/DEMO_SCRIPT.md)
- [Evaluation](docs/EVALUATION_REPORT.md)
- [Deployment](docs/DEPLOYMENT.md)
