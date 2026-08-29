"""Deterministic, evidence-linked narratives and governed recommendations."""

from __future__ import annotations

from typing import Any

from src.actions import recommended_action_ids
from src.schemas import ConfigBundle, UserEntitlement

__all__ = [
    "evidence_items",
    "finding_narrative",
    "narrative_from_packet",
    "recommended_action_ids",
]


def finding_narrative(finding: Any, user: UserEntitlement) -> str:
    """Render a role-aware finding summary with explicit uncertainty language."""

    confidence = f"{float(finding.confidence):.0%}"
    if finding.decision == "ABSTAIN":
        conclusion = (
            f"SilentSignal abstains at {confidence} evidence confidence. "
            f"{finding.requested_information} [E3]"
        )
    elif finding.decision == "ALERT":
        conclusion = (
            f"This pattern should be prioritised for human investigation; the signal is not proof of wrongdoing. "
            f"Evidence confidence is {confidence}. [E1][E2]"
        )
    else:
        conclusion = (
            f"Monitor under the governed method shown below. Evidence confidence is {confidence}, "
            f"and no high-impact action is supported. [E2][E3]"
        )

    if user.role == "compliance_head":
        perspective = (
            f"Management view: {finding.summary} Capacity and control response should remain proportional to evidence quality."
        )
    else:
        perspective = (
            f"Investigator view: {finding.summary} Preserve the evidence chain and test the stated alternative hypothesis."
        )
    return f"{perspective}\n\n{conclusion}"


def narrative_from_packet(packet: dict[str, Any]) -> str:
    """Render a persona-specific narrative using only verified packet fields."""
    finding = packet["finding"]
    confidence = packet["confidence"]["evidence_confidence"]
    role = packet["persona"]["role"]
    kpi = packet["kpi"]
    lead = (
        f"{kpi['name']} is {kpi['actual']:,.2f} versus {kpi['expected']:,.2f} expected "
        f"({kpi['change_percent']:+.1f}%)."
    )
    if role == "compliance_head":
        perspective = f"Management view: {finding['summary']} Review capacity and control response at the {packet['persona']['region_scope']} level."
    else:
        perspective = f"Investigator view: {finding['summary']} Test the linked evidence and alternative explanation before disposition."
    if finding["decision"] == "ABSTAIN":
        action = "The evidence gate requires abstention; obtain the missing information before escalation."
    elif finding["decision"] == "ALERT":
        action = "Prioritise human review. This signal is not proof of wrongdoing."
    else:
        action = "Use the configured monitoring path; no high-impact action is supported."
    return f"{lead} {perspective} Evidence confidence is {confidence:.0%}. {action} [E1][E2][E3]"


def evidence_items(finding: Any) -> list[dict[str, str]]:
    """Convert a finding into stable supporting and contradicting evidence IDs."""

    return [
        {"evidence_id": "E1", "kind": "Supporting", "statement": str(finding.supporting_evidence)},
        {"evidence_id": "E2", "kind": "Contradicting", "statement": str(finding.contradicting_evidence)},
        {"evidence_id": "E3", "kind": "Alternative / next evidence", "statement": f"{finding.alternative_hypothesis} {finding.requested_information}"},
    ]


