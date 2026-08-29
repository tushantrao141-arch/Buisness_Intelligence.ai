"""Unit tests for evidence confidence, finding generation, and abstention gates."""
import unittest
from pathlib import Path
from src.data import load_data
from src.graph_engine import build_relationships
from src.confidence import build_findings

ROOT = Path(__file__).resolve().parent.parent


class TestConfidence(unittest.TestCase):

    def setUp(self):
        self.data = load_data(ROOT)
        self.rel = build_relationships(self.data)
        self.findings = build_findings(self.data, self.rel)

    def test_findings_decisions(self):
        self.assertFalse(self.findings.empty)
        decisions = set(self.findings["decision"])
        self.assertIn("ALERT", decisions)
        self.assertIn("ABSTAIN", decisions)


if __name__ == "__main__":
    unittest.main()
