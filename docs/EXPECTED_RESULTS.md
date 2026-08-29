# Expected Results and Acceptance Scenarios

These scenarios are defined before model development. Synthetic data generation will later inject them using stable scenario IDs.

## S1 — Strong connected pattern

**Given:** Eight related new accounts perform repeated near-threshold cash activity across four branches over fourteen days and share fabricated identifiers/beneficiaries.

**Expected:**

- Near-Threshold Value Ratio rises materially.
- Related accounts form one connected cluster.
- Linked-Pattern Exposure rises.
- New-account cohort and connected branches rank among the main drivers.
- Evidence confidence is high when source freshness and mappings are complete.
- Compliance Head receives an aggregate capacity/action narrative.
- Assigned Investigator receives detailed masked evidence and an investigation action.

## S2 — Legitimate seasonal activity

**Given:** A cash-intensive business experiences a seasonal increase, has fresh KYC, expected turnover consistent with the activity, and no cross-account relationship.

**Expected:**

- Activity may contribute to a KPI movement.
- The system presents seasonal business activity as a supported alternative hypothesis.
- The engine does not conclude that the activity is coordinated wrongdoing.
- Outcome is monitor or normal review depending on configured evidence.

## S3 — Insufficient evidence

**Given:** Near-threshold activity exists, but KYC is stale, entity mappings are incomplete, and a legitimate explanation is plausible.

**Expected:**

- Evidence confidence falls below the abstention threshold or triggers a critical quality gate.
- The system requests refreshed KYC/entity mapping.
- It does not recommend high-impact escalation.

## S4 — Sparse-history channel

**Given:** `NEW_DEPOSIT` has only fourteen days of history.

**Expected:**

- The engine avoids a normal long-history baseline.
- Peer channels/branches are used when suitable.
- The result is labelled peer-based.
- Confidence is capped and the engine abstains if comparable peers are insufficient.

## S5 — Unauthorised region

**Given:** A WEST investigator requests NORTH-region entity details.

**Expected:**

- Access is denied before evidence construction.
- No restricted rows or identifiers are sent to the LLM.
- A security event is recorded.

