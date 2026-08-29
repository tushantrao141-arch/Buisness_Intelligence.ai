# KPI Manual Verification

These five fixtures are deliberately small. Each contains exactly ten rows,
the expected result is calculated by hand, and `tests/test_kpi_examples.py`
executes the same rows against the pure functions in `src/kpis.py`.

## 1. Near-Threshold Value Ratio

Illustrative threshold: ₹1,000,000. Near band: ₹800,000 inclusive to
₹1,000,000 exclusive. Transfers are outside the relevant cash denominator.

| Row | Type | Amount | In cash denominator? | In near numerator? |
|---:|---|---:|---|---|
| 1 | Cash deposit | 850,000 | Yes | Yes |
| 2 | Cash deposit | 900,000 | Yes | Yes |
| 3 | Cash withdrawal | 950,000 | Yes | Yes |
| 4 | Cash deposit | 1,100,000 | Yes | No |
| 5 | Cash deposit | 700,000 | Yes | No |
| 6 | Transfer | 900,000 | No | No |
| 7 | Transfer | 300,000 | No | No |
| 8 | Cash withdrawal | 200,000 | Yes | No |
| 9 | Cash deposit | 500,000 | Yes | No |
| 10 | Transfer | 50,000 | No | No |

Manual result: numerator = ₹2,700,000; denominator = ₹5,200,000;
`2,700,000 / 5,200,000 × 100 = 51.9230769%`.

## 2. Linked-Pattern Exposure

Ten transactions have amounts ₹100, ₹200, …, ₹1,000. The qualifying input is
`T1, T2, T2, T4`; the duplicated T2 must not be counted twice.

| ID | Amount | Qualifies after deduplication? |
|---|---:|---|
| T1 | 100 | Yes |
| T2 | 200 | Yes |
| T3 | 300 | No |
| T4 | 400 | Yes |
| T5 | 500 | No |
| T6 | 600 | No |
| T7 | 700 | No |
| T8 | 800 | No |
| T9 | 900 | No |
| T10 | 1,000 | No |

Manual result: `₹100 + ₹200 + ₹400 = ₹700`.

## 3. High-Risk Cluster Count

Internal review-score threshold: 60. A repeated cluster ID is counted once.

| Row | Cluster | Review score | Qualifies? |
|---:|---|---:|---|
| 1 | C1 | 65 | Yes |
| 2 | C1 | 72 | Yes; duplicate ID |
| 3 | C2 | 59 | No |
| 4 | C3 | 60 | Yes |
| 5 | C4 | 88 | Yes |
| 6 | C5 | 30 | No |
| 7 | C6 | 61 | Yes |
| 8 | C7 | 12 | No |
| 9 | C8 | 99 | Yes |
| 10 | C9 | 45 | No |

Manual result: distinct qualifying IDs are C1, C3, C4, C6, C8; count = `5`.

## 4. Alert Investigation Yield

Open and in-review cases are excluded because their labels are not final.

| Row | Status | Final disposition | In denominator? | Positive? |
|---:|---|---|---|---|
| 1 | Closed | Confirmed | Yes | Yes |
| 2 | Closed | Confirmed | Yes | Yes |
| 3 | Closed | Escalated | Yes | Yes |
| 4 | Closed | Cleared | Yes | No |
| 5 | Closed | Cleared | Yes | No |
| 6 | Closed | Cleared | Yes | No |
| 7 | Closed | Cleared | Yes | No |
| 8 | Closed | Confirmed | Yes | Yes |
| 9 | Open | — | No | No |
| 10 | In review | — | No | No |

Manual result: 4 positive / 8 completed × 100 = `50%`.

## 5. Case SLA Risk

As-of time: 20 August 2026 12:00 UTC. Horizon: 24 hours, inclusive. Only OPEN
and IN_REVIEW cases count.

| Row | Status | Due relative to as-of | At risk? |
|---:|---|---:|---|
| 1 | Open | +2 h | Yes |
| 2 | In review | +12 h | Yes |
| 3 | Open | +24 h | Yes |
| 4 | Open | +25 h | No |
| 5 | Closed | +4 h | No |
| 6 | In review | −1 h | No; already overdue |
| 7 | Closed | +8 h | No |
| 8 | Open | +72 h | No |
| 9 | In review | +48 h | No |
| 10 | Open | −8 h | No; already overdue |

Manual result: rows 1, 2 and 3 qualify; count = `3`.

## Interpretation boundary

Only the arithmetic is asserted here. The near band and cluster-score threshold
are governed prototype choices, not statutory thresholds or probabilities of
money laundering. Product owners must approve them before production use.

