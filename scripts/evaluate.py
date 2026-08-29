"""CLI entry point to evaluate scenarios and benchmark against baselines."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data import load_data
from src.pipeline import run_pipeline
from src.evaluation import evaluate_scenarios, compare_baselines

if __name__ == "__main__":
    data = load_data(ROOT)
    analysis = run_pipeline(data)
    eval_res = evaluate_scenarios(ROOT, analysis)
    bench, _ = compare_baselines(ROOT, data, analysis)
    print("=== SCENARIO EVALUATION ===")
    print(eval_res.to_string(index=False))
    print("\n=== BASELINE COMPARISON ===")
    print(bench[["method", "precision", "recall", "f1", "false_positives", "driver_ranking_accuracy", "abstention_correctness"]].to_string(index=False))
