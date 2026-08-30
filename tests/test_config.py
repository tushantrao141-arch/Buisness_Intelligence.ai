"""Tests for governed configuration and cross-file references."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from src.config import ConfigurationError, get_kpi, get_user, load_config_bundle
from src.schemas import UserEntitlement


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ConfigBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_config_bundle.cache_clear()
        cls.bundle = load_config_bundle(PROJECT_ROOT)

    def test_project_is_synthetic_only(self) -> None:
        self.assertTrue(self.bundle.settings.project.synthetic_data_only)
        self.assertFalse(
            self.bundle.settings.security.send_raw_identifiers_to_llm
        )

    def test_five_expected_kpis_are_configured(self) -> None:
        expected = {
            "near_threshold_value_ratio",
            "linked_pattern_exposure",
            "high_risk_cluster_count",
            "alert_investigation_yield",
            "case_sla_risk",
        }
        self.assertEqual({kpi.id for kpi in self.bundle.kpis}, expected)

    def test_kpi_contracts_are_judge_explainable(self) -> None:
        for contract in self.bundle.kpis:
            self.assertGreater(len(contract.formula), 20)
            self.assertGreaterEqual(len(contract.calculation_notes), 1)
            self.assertGreaterEqual(len(contract.lineage), 2)
            self.assertGreaterEqual(contract.materiality.z_score_threshold, 0)
            self.assertTrue(contract.access.aggregate_roles)

    def test_three_source_grains_and_cadences_are_governed(self) -> None:
        sources = self.bundle.settings.source_contracts.model_dump()
        self.assertEqual(set(sources), {"transactions", "kyc", "cases"})
        for source in sources.values():
            self.assertIn("row", source["grain"].lower())
            self.assertIn("simulated", source["refresh_cadence"].lower())

    def test_every_action_monitors_a_known_kpi(self) -> None:
        kpi_ids = {kpi.id for kpi in self.bundle.kpis}
        for action in self.bundle.actions:
            self.assertIn(action.monitoring_kpi, kpi_ids)

    def test_every_user_action_is_configured_and_role_allowed(self) -> None:
        actions = {action.id: action for action in self.bundle.actions}
        for user in self.bundle.users:
            for action_id in user.permitted_actions:
                self.assertIn(action_id, actions)
                self.assertIn(user.role, actions[action_id].allowed_roles)

    def test_named_lookup_helpers(self) -> None:
        self.assertEqual(
            get_user("west_investigator", self.bundle).regions,
            ["WEST"],
        )
        self.assertEqual(
            get_kpi("linked_pattern_exposure", self.bundle).unit,
            "INR",
        )

    def test_missing_configuration_directory_has_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            load_config_bundle.cache_clear()
            with self.assertRaises(ConfigurationError):
                load_config_bundle(temporary_directory)


class SchemaGuardrailTests(unittest.TestCase):
    def test_all_region_cannot_be_mixed_with_specific_region(self) -> None:
        with self.assertRaises(ValidationError):
            UserEntitlement(
                id="invalid_user",
                display_name="Invalid User",
                role="compliance_head",
                regions=["ALL", "WEST"],
                can_view_entity_detail=False,
                permitted_actions=[],
            )

    def test_unknown_configuration_keys_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            UserEntitlement.model_validate(
                {
                    "id": "invalid_user",
                    "display_name": "Invalid User",
                    "role": "regional_investigator",
                    "regions": ["WEST"],
                    "can_view_entity_detail": True,
                    "permitted_actions": [],
                    "unexpected_permission": True,
                }
            )


if __name__ == "__main__":
    unittest.main()

