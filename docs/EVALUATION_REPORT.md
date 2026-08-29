# Automatic Evaluation Report

Generated from `data/ground_truth/events.csv` by `src/evaluation.py`. Ground
truth is not available to KPI, movement, graph, driver, confidence, narrative,
or action code.

## Acceptance scenarios

All five predefined outcomes pass:

- S1 strong connected pattern → ALERT.
- S2 legitimate seasonal activity → MONITOR.
- S3 insufficient evidence → ABSTAIN.
- S4 sparse-history channel → PEER_BASED.
- S5 unauthorised region → ACCESS_DENIED before evidence construction.

## Four-method comparison

Alert-class metrics are calculated over S1–S4. ALERT is the positive class;
MONITOR, ABSTAIN, and PEER_BASED are negative for precision/recall and have
separate checks. The sample is intentionally tiny and proves scenario behavior,
not production generalisation.

| Method | Precision | Recall | F1 | False positives | Missed patterns | Driver accuracy | S3 abstention | Narrative numeric accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Threshold only | 0% | 0% | 0% | 0 | 1 | 0% | 0% | N/A |
| Movement detector | 50% | 100% | 66.7% | 1 | 0 | 25% | 0% | N/A |
| Movement + proximity | 50% | 100% | 66.7% | 1 | 0 | 75% | 0% | N/A |
| Full SilentSignal | 100% | 100% | 100% | 0 | 0 | 100% | 100% | 100% |

The full pipeline records zero LLM calls and zero model cost. Its measured local
end-to-end runtime is reported by `scripts/evaluate_demo.py` and the Governance
page; runtime varies by machine.

## Metric definitions

- **Precision:** true ALERT scenarios / all predicted ALERT scenarios.
- **Recall:** detected true ALERT scenarios / all true ALERT scenarios.
- **F1:** harmonic mean of precision and recall.
- **False-positive cost:** false ALERT count × ₹250,000. This is an explicit
  demonstration review-cost assumption, not a bank or regulatory estimate.
- **Missed patterns:** true ALERT scenarios not predicted as ALERT.
- **Driver-ranking accuracy:** expected S1 driver dimensions recovered by the
  method.
- **Abstention correctness:** whether S3 is explicitly ABSTAIN.
- **Narrative numerical accuracy:** whether actual, expected and percentage
  change in the narrative exactly match the structured evidence packet.

## Interpretation

The comparison shows the intended differentiation: a threshold-only method
misses repeated below-threshold activity; movement/proximity methods detect the
region but also raise the stale-data scenario; relationship and evidence gates
retain S1 while abstaining on S3.

Do not present 100% F1 as evidence of real-world model accuracy. It is 100% on
four designed analytical scenarios. A production claim requires a larger,
independently labelled, representative and held-out dataset with sensitivity
analysis and error review.

## Reproduce

```powershell
.venv\Scripts\python.exe scripts\generate_demo.py
.venv\Scripts\python.exe scripts\evaluate_demo.py
```

