# Data Specification

All data is synthetic. Identifiers are fabricated or hashed and do not represent real people.

## Source 1: Transactions

**File:** `data/raw/transactions.csv`  
**Grain:** one row per transaction  
**Simulated refresh:** every 15 minutes

| Field | Type | Required | Meaning |
|---|---|---:|---|
| transaction_id | string | yes | Unique transaction identifier |
| timestamp | datetime | yes | Event time in UTC |
| account_id | string | yes | Synthetic account identifier |
| amount_inr | float | yes | Positive transaction amount in INR |
| branch_id | string | yes | Originating branch |
| region | string | yes | NORTH, SOUTH, EAST, or WEST |
| channel | string | yes | BRANCH_CASH, ATM, ONLINE, or NEW_DEPOSIT |
| transaction_type | string | yes | CASH_DEPOSIT, CASH_WITHDRAWAL, or TRANSFER |
| beneficiary_hash | string | no | Synthetic hashed beneficiary relationship |

## Source 2: KYC and accounts

**File:** `data/raw/kyc.csv`  
**Grain:** one row per account snapshot  
**Simulated refresh:** daily

| Field | Type | Required | Meaning |
|---|---|---:|---|
| customer_id | string | yes | Synthetic customer identifier |
| account_id | string | yes | Synthetic account identifier |
| business_type | string | yes | Customer activity category |
| risk_tier | string | yes | LOW, MEDIUM, or HIGH |
| expected_monthly_turnover_inr | float | yes | Simulated expected turnover |
| account_open_date | date | yes | Account start date |
| phone_hash | string | no | Fabricated shared-identifier hash |
| address_hash | string | no | Fabricated shared-identifier hash |
| kyc_updated_at | datetime | yes | Last KYC refresh time |

## Source 3: Investigation cases

**File:** `data/raw/cases.csv`  
**Grain:** one row per case status event  
**Simulated refresh:** every four hours

| Field | Type | Required | Meaning |
|---|---|---:|---|
| case_id | string | yes | Unique investigation case |
| cluster_id | string | no | Related detected cluster |
| status | string | yes | OPEN, IN_REVIEW, CLOSED_CONFIRMED, or CLOSED_CLEARED |
| assigned_investigator | string | no | Synthetic user ID |
| region | string | yes | Case region |
| opened_at | datetime | yes | Case opening time |
| sla_due_at | datetime | yes | Investigation deadline |
| final_disposition | string | no | Confirmed, cleared, or unresolved result |

## Source metadata

`data/raw/source_metadata.json` records each source's generation time, simulated last refresh, expected refresh SLA, row count, and schema version.

## Ground truth

`data/ground_truth/events.csv` describes injected scenarios and their expected outcomes. Analytical modules must never use this file as an input. Only evaluation code may read it.

## Data-quality rules

- Duplicate `transaction_id` values are rejected.
- Negative or zero transaction amounts are rejected.
- Unknown regions are quarantined.
- Unmatched accounts are retained with a data-quality flag.
- KYC freshness is compared with the configured freshness SLA.
- Source timestamps must not be later than the analytical `as_of` time.
- Every transformation preserves the original transaction ID for traceability.

