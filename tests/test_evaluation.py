"""Unit and acceptance tests for the held-out evaluation module."""
import unittest
from pathlib import Path
from src.data import load_data
from src.pipeline import run_pipeline
from src.evaluation import evaluate_scenarios, compare_baselines, evaluation_summary

ROOT = Path(__file__).resolve().parent.parent


class TestEvaluation(unittest.TestCase):

    def setUp(self):
        self.data = load_data(ROOT)
        self.analysis = run_pipeline(self.data)

    def test_golden_scenarios_s1_through_s5(self):
        """All 5 acceptance scenarios match expected ground truth decisions."""
        results = evaluate_scenarios(ROOT, self.analysis)
        self.assertEqual(len(results), 5)
        passed_count = int(results["passed"].sum())
        self.assertEqual(passed_count, 5, f"Expected 5/5 passed scenarios, got {passed_count}")

    def test_baseline_comparator_metrics(self):
        """SilentSignal outperforms single-rule and movement-only baselines."""
        bench, detail = compare_baselines(ROOT, self.data, self.analysis)
        self.assertEqual(len(bench), 4)

        ss_row = bench.loc[bench["method"] == "Full SilentSignal"].iloc[0]
        self.assertEqual(ss_row["precision"], 1.0)
        self.assertEqual(ss_row["recall"], 1.0)
        self.assertEqual(ss_row["f1"], 1.0)
        self.assertEqual(ss_row["false_positives"], 0)
        self.assertEqual(ss_row["abstention_correctness"], 1.0)
        self.assertEqual(ss_row["driver_ranking_accuracy"], 1.0)

    def test_evaluation_summary(self):
        results = evaluate_scenarios(ROOT, self.analysis)
        summary = evaluation_summary(results)
        self.assertEqual(summary["passed"], 5)
        self.assertEqual(summary["acceptance_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
