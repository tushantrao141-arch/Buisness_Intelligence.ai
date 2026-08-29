"""Script to generate reproducible synthetic data sources."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_generator import generate_synthetic_data

if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    counts = generate_synthetic_data(ROOT, force=force)
    print(f"Generated synthetic data: {counts['transactions']:,} transactions, {counts['kyc']:,} KYC records, {counts['cases']:,} cases.")
