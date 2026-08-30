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

    def test_connected_pattern_queue_excludes_diffuse_graph_noise(self):
        connected = self.findings.loc[self.findings["finding_type"].eq("Connected pattern")]
        self.assertEqual(len(connected), 1)
        self.assertEqual(connected.iloc[0]["title"], "8-account connected cash pattern")


if __name__ == "__main__":
    unittest.main()
