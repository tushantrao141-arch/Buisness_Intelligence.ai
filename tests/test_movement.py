"""Unit tests for historical baselines and movement detection."""
import unittest
from pathlib import Path
from src.data import load_data
from src.config import get_kpi, load_config_bundle
from src.graph_engine import build_relationships
from src.movement import build_kpi_history, detect_movements, passes_materiality_rule

ROOT = Path(__file__).resolve().parent.parent


class TestMovement(unittest.TestCase):

    def setUp(self):
        self.data = load_data(ROOT)
        self.rel = build_relationships(self.data)
        self.history = build_kpi_history(self.data, self.rel)
        self.movements = detect_movements(self.history)

    def test_movements_calculated_for_all_regions_and_kpis(self):
        self.assertFalse(self.movements.empty)
        regions = set(self.movements["region"])
        self.assertIn("ALL", regions)
        self.assertIn("WEST", regions)
        self.assertIn("NORTH", regions)
        self.assertIn("EAST", regions)
        self.assertIn("SOUTH", regions)

    def test_movement_schema_columns(self):
        expected_cols = {"region", "kpi_id", "actual", "expected", "delta", "delta_pct", "z_score", "material", "priority_score", "priority"}
        self.assertTrue(expected_cols.issubset(set(self.movements.columns)))

    def test_materiality_thresholds_come_from_kpi_contracts(self):
        bundle = load_config_bundle(ROOT)
        ratio_rule = get_kpi("near_threshold_value_ratio", bundle).materiality
        exposure_rule = get_kpi("linked_pattern_exposure", bundle).materiality
        self.assertTrue(passes_materiality_rule(5, 1.5, ratio_rule))
        self.assertFalse(passes_materiality_rule(4.9, 1.5, ratio_rule))
        self.assertFalse(passes_materiality_rule(5_000_000, 1.5, exposure_rule))
        self.assertTrue(passes_materiality_rule(5_000_001, 1.5, exposure_rule))


if __name__ == "__main__":
    unittest.main()
