"""Unit tests for behavioral feature engineering."""
import unittest
from pathlib import Path
from src.data import load_data
from src.features import derive_behavioral_features

ROOT = Path(__file__).resolve().parent.parent


class TestFeatures(unittest.TestCase):

    def setUp(self):
        self.data = load_data(ROOT)

    def test_derived_features_exist(self):
        enriched = derive_behavioral_features(self.data.transactions, self.data.kyc, self.data.as_of)
        self.assertIn("is_near_threshold", enriched.columns)
        self.assertIn("account_age_band", enriched.columns)
        self.assertIn("kyc_fresh", enriched.columns)
        self.assertIn("mapping_complete", enriched.columns)
        self.assertIn("velocity_7d", enriched.columns)
        self.assertIn("branch_hop_3d", enriched.columns)
        self.assertIn("turnover_deviation_ratio", enriched.columns)


if __name__ == "__main__":
    unittest.main()
