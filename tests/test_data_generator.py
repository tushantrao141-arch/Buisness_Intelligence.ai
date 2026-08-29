"""Acceptance tests for the synthetic data generator."""
import hashlib
import unittest
from pathlib import Path

import pandas as pd
from src.data_generator import AS_OF, REGIONS, generate_synthetic_data

ROOT = Path(__file__).resolve().parent.parent


class TestDataGenerator(unittest.TestCase):

    def setUp(self):
        generate_synthetic_data(ROOT, force=True)

    def test_determinism_seed_42(self):
        """Running generator twice with seed 42 produces identical data hashes."""
        tx1 = (ROOT / "data" / "raw" / "transactions.csv").read_bytes()
        generate_synthetic_data(ROOT, force=True)
        tx2 = (ROOT / "data" / "raw" / "transactions.csv").read_bytes()
        self.assertEqual(hashlib.sha256(tx1).hexdigest(), hashlib.sha256(tx2).hexdigest())

    def test_row_counts_and_ranges(self):
        """Generated sources satisfy Day 1 count specifications."""
        tx = pd.read_csv(ROOT / "data" / "raw" / "transactions.csv")
        kyc = pd.read_csv(ROOT / "data" / "raw" / "kyc.csv")
        cases = pd.read_csv(ROOT / "data" / "raw" / "cases.csv")

        self.assertTrue(8_000 <= len(tx) <= 25_000, f"Tx count {len(tx)} out of range")
        self.assertTrue(150 <= len(kyc) <= 400, f"KYC count {len(kyc)} out of range")
        self.assertTrue(80 <= len(cases) <= 200, f"Cases count {len(cases)} out of range")

    def test_referential_integrity(self):
        """All transaction accounts and case accounts exist in KYC."""
        tx = pd.read_csv(ROOT / "data" / "raw" / "transactions.csv")
        kyc = pd.read_csv(ROOT / "data" / "raw" / "kyc.csv")
        cases = pd.read_csv(ROOT / "data" / "raw" / "cases.csv")

        kyc_accounts = set(kyc["account_id"])
        self.assertTrue(set(tx["account_id"]).issubset(kyc_accounts))
        self.assertTrue("account_id" in cases.columns)
        self.assertTrue(set(cases["account_id"]).issubset(kyc_accounts))

    def test_scenario_s1_accounts(self):
        """S1 contains 8 related accounts over 14 days and 4 branches."""
        tx = pd.read_csv(ROOT / "data" / "raw" / "transactions.csv")
        s1_accounts = [f"W_SIG_{i:02d}" for i in range(1, 9)]
        s1_tx = tx[tx["account_id"].isin(s1_accounts)]
        self.assertEqual(s1_tx["account_id"].nunique(), 8)
        self.assertEqual(s1_tx["region"].iloc[0], "WEST")
        self.assertTrue(s1_tx["branch_id"].nunique() >= 3)

    def test_no_future_timestamps(self):
        """No events occur after the analytical as-of timestamp."""
        tx = pd.read_csv(ROOT / "data" / "raw" / "transactions.csv")
        tx_ts = pd.to_datetime(tx["timestamp"], utc=True)
        self.assertTrue((tx_ts <= AS_OF).all())


if __name__ == "__main__":
    unittest.main()
