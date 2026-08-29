"""End-to-end deterministic analytics and acceptance tests."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.runtime import build_demo


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = build_demo(PROJECT_ROOT, force_regenerate=True, persist_telemetry=False)

    def test_all_five_kpis_have_history_for_every_scope(self) -> None:
        history = self.runtime.analysis.history
        self.assertEqual(history["kpi_id"].nunique(), 5)
        self.assertEqual(set(history["region"].unique()), {"ALL", "NORTH", "SOUTH", "EAST", "WEST"})

    def test_no_critical_data_quality_failures(self) -> None:
        critical = self.runtime.data.quality.loc[self.runtime.data.quality["severity"].eq("critical"), "affected_rows"].sum()
        self.assertEqual(int(critical), 0)

    def test_connected_pattern_is_alerted_with_high_confidence(self) -> None:
        findings = self.runtime.analysis.findings
        target = findings.loc[
            findings["account_ids"].map(lambda values: "W_SIG_01" in values)
        ].iloc[0]
        self.assertEqual(target["decision"], "ALERT")
        self.assertGreaterEqual(target["confidence"], 0.75)
        self.assertEqual(target["finding_type"], "Connected pattern")

    def test_evidence_gap_abstains(self) -> None:
        findings = self.runtime.analysis.findings
        target = findings.loc[
            findings["account_ids"].map(lambda values: "N_GAP_01" in values)
        ].iloc[0]
        self.assertEqual(target["decision"], "ABSTAIN")
        self.assertLess(target["confidence"], 0.60)

    def test_sparse_channel_is_peer_based(self) -> None:
        finding = self.runtime.analysis.findings.set_index("finding_id").loc["SPARSE-NEW_DEPOSIT"]
        self.assertEqual(finding["decision"], "PEER_BASED")
        self.assertIn("Peer", finding["method"])

    def test_all_predefined_acceptance_scenarios_pass(self) -> None:
        self.assertTrue(self.runtime.evaluation["passed"].all(), self.runtime.evaluation.to_dict("records"))

    def test_cluster_exposure_uses_unique_transaction_ids(self) -> None:
        memberships = self.runtime.analysis.relationships.transaction_clusters
        self.assertFalse(memberships["transaction_id"].duplicated().any())

    def test_heterogeneous_graph_contains_required_entity_types(self) -> None:
        graph = self.runtime.analysis.relationships.heterogeneous_graph
        entity_types = {attributes["entity_type"] for _, attributes in graph.nodes(data=True)}
        self.assertTrue({"customer", "account", "transaction", "beneficiary", "branch"}.issubset(entity_types))

    def test_driver_contributions_reconcile_to_movement(self) -> None:
        drivers = self.runtime.analysis.drivers
        grouped = drivers.groupby(["region", "kpi_id"], as_index=False).agg(
            contribution=("contribution", "sum"),
            movement=("movement_total", "first"),
            unexplained=("unexplained", "first"),
        )
        self.assertTrue(((grouped["contribution"] - grouped["movement"]).abs() < 1e-6).all())
        self.assertTrue((grouped["unexplained"].abs() < 1e-6).all())

    def test_four_baselines_are_calculated_from_ground_truth(self) -> None:
        benchmark = self.runtime.benchmark.set_index("method")
        self.assertEqual(len(benchmark), 4)
        self.assertEqual(benchmark.loc["Threshold only", "recall"], 0.0)
        self.assertEqual(benchmark.loc["Full SilentSignal", "f1"], 1.0)
        self.assertEqual(benchmark.loc["Full SilentSignal", "abstention_correctness"], 1.0)
        self.assertGreaterEqual(benchmark["false_positive_cost_inr"].max(), 0)


if __name__ == "__main__":
    unittest.main()
