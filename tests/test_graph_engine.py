"""Unit tests for graph engine and cluster identification."""
import unittest
from pathlib import Path
from src.data import load_data
from src.graph_engine import build_relationships

ROOT = Path(__file__).resolve().parent.parent


class TestGraphEngine(unittest.TestCase):

    def setUp(self):
        self.data = load_data(ROOT)
        self.rel = build_relationships(self.data)

    def test_s1_forms_connected_component(self):
        s1_accounts = {f"W_SIG_{i:02d}" for i in range(1, 9)}
        found = any(s1_accounts.issubset(set(cluster.account_ids)) for cluster in self.rel.clusters.itertuples())
        self.assertTrue(found, "S1 accounts must form a single connected component cluster")

    def test_s2_remains_isolated(self):
        s2 = "E_SEASONAL_01"
        found = any(s2 in cluster.account_ids for cluster in self.rel.clusters.itertuples())
        self.assertFalse(found, "S2 account must not belong to any connected cluster")


if __name__ == "__main__":
    unittest.main()
