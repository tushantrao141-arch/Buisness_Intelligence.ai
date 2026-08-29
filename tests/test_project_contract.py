"""Tests that keep written specifications and configuration aligned."""

from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProjectContractTests(unittest.TestCase):
    def test_required_specs_exist_and_are_not_empty(self) -> None:
        required = [
            "PRODUCT_SPEC.md",
            "DATA_SPEC.md",
            "KPI_SPEC.md",
            "EXPECTED_RESULTS.md",
            "REQUIREMENTS_MATRIX.md",
            "BUILD_STATUS.md",
        ]
        for filename in required:
            path = PROJECT_ROOT / "docs" / filename
            self.assertTrue(path.exists(), filename)
            self.assertGreater(path.stat().st_size, 100, filename)

    def test_demo_sources_are_generated(self) -> None:
        expected = {"transactions.csv", "kyc.csv", "cases.csv"}
        generated = {path.name for path in (PROJECT_ROOT / "data" / "raw").glob("*.csv")}
        self.assertEqual(generated, expected)
        self.assertTrue((PROJECT_ROOT / "data" / "raw" / "source_metadata.json").exists())

    def test_streamlit_pages_exist(self) -> None:
        page_files = list((PROJECT_ROOT / "pages").glob("*.py"))
        self.assertEqual(len(page_files), 5)

    def test_full_analytical_modules_exist(self) -> None:
        expected = {
            "analytics.py",
            "data.py",
            "data_generator.py",
            "evaluation.py",
            "evidence.py",
            "kpis.py",
            "narrative.py",
            "runtime.py",
            "security.py",
            "storage.py",
        }
        available = {path.name for path in (PROJECT_ROOT / "src").glob("*.py")}
        self.assertTrue(expected.issubset(available))

    def test_judge_and_owner_documents_exist(self) -> None:
        expected = {"OWNER_HANDBOOK.md", "KPI_MANUAL_VERIFICATION.md", "EVALUATION_REPORT.md", "BUILD_PLAYBOOK.md", "DEMO_SCRIPT.md", "DEPLOYMENT.md"}
        available = {path.name for path in (PROJECT_ROOT / "docs").glob("*.md")}
        self.assertTrue(expected.issubset(available))


if __name__ == "__main__":
    unittest.main()
