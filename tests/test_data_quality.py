"""Unit tests for data quality and validation layer."""
import unittest
from pathlib import Path

import pandas as pd
from src.data_generator import generate_synthetic_data
from src.data_quality import validate_and_process_data

ROOT = Path(__file__).resolve().parent.parent


class TestDataQuality(unittest.TestCase):

    def setUp(self):
        generate_synthetic_data(ROOT, force=True)

    def test_validation_and_parquet_output(self):
        """Data quality validation passes and writes Parquet files."""
        report = validate_and_process_data(ROOT)
        self.assertEqual(report.critical_failures, 0)
        self.assertGreaterEqual(report.quality_score, 0.9)

        proc_dir = ROOT / "data" / "processed"
        self.assertTrue((proc_dir / "transactions.parquet").exists())
        self.assertTrue((proc_dir / "kyc.parquet").exists())
        self.assertTrue((proc_dir / "cases.parquet").exists())

        tx_pq = pd.read_parquet(proc_dir / "transactions.parquet")
        self.assertGreater(len(tx_pq), 1000)


if __name__ == "__main__":
    unittest.main()
