"""Governed next-best action recommendations matching action playbooks."""

from __future__ import annotations

from typing import Any
from src.schemas import ConfigBundle, UserEntitlement


def recommended_action_ids(finding: Any, user: UserEntitlement, bundle: ConfigBundle) -> list[str]:
    """Return only authorized action IDs permitted for the user's role and finding state."""
    decision = getattr(finding, "decision", finding.get("decision") if isinstance(finding, dict) else "")
    finding_type = getattr(finding, "finding_type", finding.get("finding_type") if isinstance(finding, dict) else "")

    candidates: list[str] = []
    if decision == "ABSTAIN":
        candidates = ["request_kyc_refresh"]
    elif finding_type == "Connected pattern":
        if user.role == "compliance_head":
            candidates = ["allocate_investigation_capacity", "request_kyc_refresh"]
        else:
            candidates = ["consolidate_linked_events", "request_kyc_refresh"]
    elif finding_type == "Alternative hypothesis":
        candidates = ["monitor_seasonal_activity"]

    configured = {action.id for action in bundle.actions}
    return [
        action_id
        for action_id in candidates
        if action_id in configured and action_id in user.permitted_actions
    ]
