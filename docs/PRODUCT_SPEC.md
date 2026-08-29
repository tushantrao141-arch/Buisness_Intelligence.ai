# Product Specification

## Product

**Name:** BusinessIntelligence.ai — SilentSignal

**One-sentence description:** SilentSignal helps a bank compliance team decide which risk pattern requires attention, why it became material, how trustworthy the explanation is, and what authorised action should happen next.

## Business problem

Traditional dashboards report that a KPI moved but usually do not reconcile fragmented data, rank the explanatory drivers, communicate uncertainty, or recommend a governed action. Single-transaction monitoring can also under-prioritise activity whose important meaning appears only after relationships and timing are considered together.

## Primary decision

Which KPI movement or connected activity pattern should be investigated first, and what is the next permitted action for the current user?

## Users

### Compliance Head

Needs aggregate exposure, regional contribution, operational capacity, confidence, and management actions. This user can view all regions but receives masked or aggregated customer information by default.

### Regional AML Investigator

Needs assigned-region transaction evidence, connected entities, timing patterns, missing information, alternative hypotheses, and case-level investigation steps.

## Inputs

1. Synthetic transaction events refreshed every 15 minutes.
2. Synthetic KYC/account snapshots refreshed daily.
3. Synthetic investigation case events refreshed every four hours.

## Outputs

- Prioritised KPI movements.
- Ranked explanatory drivers with contributions.
- Connected entity/transaction clusters.
- Evidence freshness and lineage.
- Evidence-confidence result.
- Persona-specific narrative or abstention.
- Approved action, owner, expected impact, and monitoring plan.
- Feedback and runtime telemetry.

## Required demo scenarios

1. Strong multi-factor movement with a connected SilentSignal pattern.
2. Legitimate seasonal activity that must not be treated as a conclusion of wrongdoing.
3. Low-confidence scenario that requests missing information and abstains.
4. Sparse-history scenario using peer comparison.
5. Role-based denial for a user requesting an unauthorised region.

## Non-goals

- Production banking integration.
- Real customer or account data.
- Automatic account freezing or regulatory filing.
- A legal conclusion about a customer.
- A graph neural network or complex causal-inference system.
- An LLM that calculates KPIs or invents quantitative truth.
- Production identity-provider integration.

## Success criteria

- All five KPIs match hand-verifiable unit tests.
- Injected ground-truth scenarios produce the expected alert, monitor, or abstain outcome.
- Every narrative claim references evidence.
- An unauthorised query is rejected before evidence construction or LLM use.
- The application remains demonstrable when the LLM is unavailable.
- Evaluation and runtime results are calculated, not typed manually.

