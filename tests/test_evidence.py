"""Evidence-packet traceability and pre-construction access tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.config import get_user, load_config_bundle
from src.evidence import build_evidence_packet, llm_payload
from src.narrative import narrative_from_packet
from src.runtime import build_demo
from src.security import AccessDenied


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class EvidencePacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = load_config_bundle(PROJECT_ROOT)
        cls.runtime = build_demo(PROJECT_ROOT, persist_telemetry=False)
        cls.west_finding = cls.runtime.analysis.findings.loc[
            cls.runtime.analysis.findings["account_ids"].map(lambda values: "W_SIG_01" in values)
        ].iloc[0]

    def test_packet_contains_all_governed_sections_and_no_raw_ids(self) -> None:
        user = get_user("west_investigator", self.bundle)
        packet = build_evidence_packet(self.runtime.data, self.runtime.analysis, self.bundle, user, "WEST", self.west_finding["finding_id"])
        expected = {"kpi", "drivers", "driver_reconciliation", "source_freshness", "missing_data", "analytical_method", "confidence", "alternative_hypothesis", "evidence", "permitted_actions"}
        self.assertTrue(expected.issubset(packet))
        serialized = json.dumps(llm_payload(packet))
        self.assertNotIn("W_SIG_01", serialized)
        self.assertFalse(packet["guardrails"]["raw_identifiers_present"])

    def test_aggregate_persona_receives_no_entity_list(self) -> None:
        user = get_user("compliance_head", self.bundle)
        packet = build_evidence_packet(self.runtime.data, self.runtime.analysis, self.bundle, user, "WEST", self.west_finding["finding_id"])
        self.assertEqual(packet["entity_scope"]["detail_level"], "aggregate only")
        self.assertNotIn("masked_accounts", packet["entity_scope"])

    def test_unauthorised_scope_fails_before_finding_lookup(self) -> None:
        user = get_user("west_investigator", self.bundle)
        with self.assertRaises(AccessDenied):
            build_evidence_packet(self.runtime.data, self.runtime.analysis, self.bundle, user, "NORTH", "does-not-exist")

    def test_narrative_numbers_come_from_packet(self) -> None:
        user = get_user("west_investigator", self.bundle)
        packet = build_evidence_packet(self.runtime.data, self.runtime.analysis, self.bundle, user, "WEST", self.west_finding["finding_id"])
        narrative = narrative_from_packet(packet)
        self.assertIn(f"{packet['kpi']['actual']:,.2f}", narrative)
        self.assertIn("[E1][E2][E3]", narrative)


if __name__ == "__main__":
    unittest.main()

