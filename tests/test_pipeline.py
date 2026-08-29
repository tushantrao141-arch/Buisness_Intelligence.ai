"""Integration test for full end-to-end analytical pipeline."""
import unittest
from pathlib import Path
from src.data import load_data
from src.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parent.parent


class TestPipeline(unittest.TestCase):

    def test_pipeline_execution(self):
        data = load_data(ROOT)
        result = run_pipeline(data)
        self.assertFalse(result.history.empty)
        self.assertFalse(result.movements.empty)
        self.assertFalse(result.drivers.empty)
        self.assertFalse(result.findings.empty)
        self.assertIsNotNone(result.relationships.graph)


if __name__ == "__main__":
    unittest.main()
