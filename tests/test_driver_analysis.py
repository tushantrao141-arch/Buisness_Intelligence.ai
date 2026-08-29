"""Unit tests for driver contribution reconciliation."""
import unittest
from pathlib import Path
from src.data import load_data
from src.graph_engine import build_relationships
from src.driver_analysis import calculate_drivers

ROOT = Path(__file__).resolve().parent.parent


class TestDriverAnalysis(unittest.TestCase):

    def setUp(self):
        self.data = load_data(ROOT)
        self.rel = build_relationships(self.data)
        self.drivers = calculate_drivers(self.data, self.rel)

    def test_drivers_reconcile_within_tolerance(self):
        self.assertFalse(self.drivers.empty)
        unreconciled = self.drivers.loc[~self.drivers["reconciles"]]
        self.assertEqual(len(unreconciled), 0, "All driver contributions must reconcile to total movement")


if __name__ == "__main__":
    unittest.main()
