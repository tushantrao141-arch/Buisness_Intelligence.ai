"""Unit tests for the five governed KPI calculation formulas."""
import unittest
import pandas as pd
from src.kpi_engine import (
    near_threshold_value_ratio,
    linked_pattern_exposure,
    high_risk_cluster_count,
    alert_investigation_yield,
    case_sla_risk,
)


class TestKPIEngine(unittest.TestCase):

    def test_near_threshold_value_ratio(self):
        tx = pd.DataFrame([
            {"transaction_type": "CASH_DEPOSIT", "amount_inr": 900_000},
            {"transaction_type": "CASH_WITHDRAWAL", "amount_inr": 100_000},
            {"transaction_type": "TRANSFER", "amount_inr": 500_000},
        ])
        ratio = near_threshold_value_ratio(tx)
        self.assertEqual(ratio, 90.0)

    def test_linked_pattern_exposure_unique_tx(self):
        tx = pd.DataFrame([
            {"transaction_id": "TX1", "amount_inr": 100_000},
            {"transaction_id": "TX1", "amount_inr": 100_000},  # duplicate
            {"transaction_id": "TX2", "amount_inr": 200_000},
        ])
        exposure = linked_pattern_exposure(tx, {"TX1", "TX2"})
        self.assertEqual(exposure, 300_000)

    def test_high_risk_cluster_count(self):
        clusters = pd.DataFrame([
            {"cluster_id": "C1", "review_score": 75},
            {"cluster_id": "C1", "review_score": 75},
            {"cluster_id": "C2", "review_score": 50},
        ])
        count = high_risk_cluster_count(clusters, review_score_threshold=60)
        self.assertEqual(count, 1)

    def test_alert_investigation_yield(self):
        cases = pd.DataFrame([
            {"status": "CLOSED_CONFIRMED", "final_disposition": "CONFIRMED"},
            {"status": "CLOSED_CLEARED", "final_disposition": "CLEARED"},
            {"status": "OPEN", "final_disposition": ""},
        ])
        yield_pct = alert_investigation_yield(cases)
        self.assertEqual(yield_pct, 50.0)

    def test_case_sla_risk(self):
        as_of = pd.Timestamp("2026-08-20T12:00:00Z")
        cases = pd.DataFrame([
            {"status": "OPEN", "sla_due_at": "2026-08-20T18:00:00Z"},
            {"status": "IN_REVIEW", "sla_due_at": "2026-08-21T06:00:00Z"},
            {"status": "OPEN", "sla_due_at": "2026-08-25T12:00:00Z"},
            {"status": "CLOSED_CONFIRMED", "sla_due_at": "2026-08-20T15:00:00Z"},
        ])
        risk_count = case_sla_risk(cases, as_of, horizon_hours=24)
        self.assertEqual(risk_count, 2)


if __name__ == "__main__":
    unittest.main()
