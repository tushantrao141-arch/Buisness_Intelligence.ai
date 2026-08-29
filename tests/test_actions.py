"""Unit tests for role-permitted action recommendations."""
import unittest
from pathlib import Path
from src.config import load_config_bundle, get_user
from src.actions import recommended_action_ids

ROOT = Path(__file__).resolve().parent.parent


class TestActions(unittest.TestCase):

    def setUp(self):
        self.bundle = load_config_bundle(ROOT)
        self.compliance_head = get_user("compliance_head", self.bundle)
        self.west_investigator = get_user("west_investigator", self.bundle)

    def test_abstention_recommends_kyc_refresh(self):
        finding = {"decision": "ABSTAIN", "finding_type": "Evidence gap"}
        actions = recommended_action_ids(finding, self.compliance_head, self.bundle)
        self.assertEqual(actions, ["request_kyc_refresh"])

    def test_connected_pattern_actions_differ_by_role(self):
        finding = {"decision": "ALERT", "finding_type": "Connected pattern"}
        head_actions = recommended_action_ids(finding, self.compliance_head, self.bundle)
        inv_actions = recommended_action_ids(finding, self.west_investigator, self.bundle)

        self.assertIn("allocate_investigation_capacity", head_actions)
        self.assertIn("consolidate_linked_events", inv_actions)
        self.assertNotIn("consolidate_linked_events", head_actions)


if __name__ == "__main__":
    unittest.main()
