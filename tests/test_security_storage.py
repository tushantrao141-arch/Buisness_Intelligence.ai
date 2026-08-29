"""Security boundary and durable event-store tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.config import get_user, load_config_bundle
from src.security import AccessDenied, check_access, enforce_access, mask_identifier
from src.storage import read_events, record_action, record_feedback, record_runtime, record_security


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = load_config_bundle(PROJECT_ROOT)

    def test_unauthorised_region_is_denied(self) -> None:
        user = get_user("west_investigator", self.bundle)
        decision = check_access(user, "NORTH", detail=True)
        self.assertFalse(decision.allowed)
        with self.assertRaises(AccessDenied):
            enforce_access(user, "NORTH", detail=True)

    def test_compliance_head_cannot_view_entity_detail(self) -> None:
        user = get_user("compliance_head", self.bundle)
        self.assertFalse(check_access(user, "WEST", detail=True).allowed)
        self.assertTrue(check_access(user, "WEST", detail=False).allowed)

    def test_masking_does_not_return_raw_identifier(self) -> None:
        masked = mask_identifier("W_SIG_01")
        self.assertNotEqual(masked, "W_SIG_01")
        self.assertTrue(masked.endswith("G_01"))


class StorageTests(unittest.TestCase):
    def test_all_event_types_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            record_runtime(root, 123.4)
            record_action(root, "tester", "F1", "A1")
            record_feedback(root, "tester", "F1", "Useful", "Clear", "Correct", "branch", "Accepted", "regional_investigator")
            record_security(root, "tester", "NORTH", "ACCESS_DENIED", "test")
            self.assertEqual(len(read_events(root, "runtime_events")), 1)
            self.assertEqual(len(read_events(root, "action_events")), 1)
            feedback = read_events(root, "feedback_events")
            self.assertEqual(len(feedback), 1)
            self.assertEqual(feedback.iloc[0]["correctness"], "Correct")
            self.assertEqual(feedback.iloc[0]["action_decision"], "Accepted")
            self.assertEqual(len(read_events(root, "security_events")), 1)


if __name__ == "__main__":
    unittest.main()
