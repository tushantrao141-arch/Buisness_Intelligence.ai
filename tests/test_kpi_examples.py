"""Ten-row manual examples for every KPI contract."""

from __future__ import annotations

import unittest
import pandas as pd

from src.kpis import alert_investigation_yield, case_sla_risk, high_risk_cluster_count, linked_pattern_exposure, near_threshold_value_ratio


class ManualKPIExamples(unittest.TestCase):
    def test_near_threshold_value_ratio_ten_rows(self) -> None:
        frame = pd.DataFrame({"transaction_type": ["CASH_DEPOSIT", "CASH_DEPOSIT", "CASH_WITHDRAWAL", "CASH_DEPOSIT", "CASH_DEPOSIT", "TRANSFER", "TRANSFER", "CASH_WITHDRAWAL", "CASH_DEPOSIT", "TRANSFER"], "amount_inr": [850_000, 900_000, 950_000, 1_100_000, 700_000, 900_000, 300_000, 200_000, 500_000, 50_000]})
        self.assertAlmostEqual(near_threshold_value_ratio(frame), 2_700_000 / 5_200_000 * 100)

    def test_linked_pattern_exposure_ten_rows(self) -> None:
        frame = pd.DataFrame({"transaction_id": [f"T{i}" for i in range(1, 11)], "amount_inr": [i * 100 for i in range(1, 11)]})
        self.assertEqual(linked_pattern_exposure(frame, ["T1", "T2", "T2", "T4"]), 700)

    def test_high_risk_cluster_count_ten_rows(self) -> None:
        frame = pd.DataFrame({"cluster_id": ["C1", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"], "review_score": [65, 72, 59, 60, 88, 30, 61, 12, 99, 45]})
        self.assertEqual(high_risk_cluster_count(frame), 5)

    def test_alert_investigation_yield_ten_rows(self) -> None:
        frame = pd.DataFrame({"status": ["CLOSED_CONFIRMED", "CLOSED_CONFIRMED", "CLOSED_CONFIRMED", "CLOSED_CLEARED", "CLOSED_CLEARED", "CLOSED_CLEARED", "CLOSED_CLEARED", "CLOSED_CONFIRMED", "OPEN", "IN_REVIEW"], "final_disposition": ["CONFIRMED", "CONFIRMED", "ESCALATED", "CLEARED", "CLEARED", "CLEARED", "CLEARED", "CONFIRMED", "", ""]})
        self.assertEqual(alert_investigation_yield(frame), 50.0)

    def test_case_sla_risk_ten_rows(self) -> None:
        as_of = pd.Timestamp("2026-08-20T12:00:00Z")
        frame = pd.DataFrame({"status": ["OPEN", "IN_REVIEW", "OPEN", "OPEN", "CLOSED_CLEARED", "IN_REVIEW", "CLOSED_CONFIRMED", "OPEN", "IN_REVIEW", "OPEN"], "sla_due_at": [as_of + pd.Timedelta(hours=2), as_of + pd.Timedelta(hours=12), as_of + pd.Timedelta(hours=24), as_of + pd.Timedelta(hours=25), as_of + pd.Timedelta(hours=4), as_of - pd.Timedelta(hours=1), as_of + pd.Timedelta(hours=8), as_of + pd.Timedelta(hours=72), as_of + pd.Timedelta(hours=48), as_of - pd.Timedelta(hours=8)]})
        self.assertEqual(case_sla_risk(frame, as_of), 3)


if __name__ == "__main__":
    unittest.main()

