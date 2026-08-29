"""CLI entry point to execute the SilentSignal pipeline."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data import load_data
from src.pipeline import run_pipeline

if __name__ == "__main__":
    print("Loading data...")
    data = load_data(ROOT)
    print("Running analytical pipeline...")
    result = run_pipeline(data)
    print(f"Pipeline executed successfully: {len(result.movements)} movements, {len(result.findings)} findings.")
