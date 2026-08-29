"""Role and region enforcement that runs before evidence construction."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.schemas import UserEntitlement


@dataclass(frozen=True)
class AccessDecision:
    """Authorization outcome with a human-readable policy reason."""

    allowed: bool
    reason: str


class AccessDenied(PermissionError):
    """Raised before restricted data is filtered or evidence is constructed."""


def check_access(user: UserEntitlement, region: str, detail: bool = False) -> AccessDecision:
    """Evaluate region and detail access without reading restricted data."""

    region_allowed = "ALL" in user.regions or region in user.regions
    if not region_allowed:
        return AccessDecision(False, f"{user.display_name} is not entitled to {region} data.")
    if detail and not user.can_view_entity_detail:
        return AccessDecision(False, f"{user.display_name} may view aggregate information only.")
    return AccessDecision(True, "Access permitted by configured role and region policy.")


def enforce_access(user: UserEntitlement, region: str, detail: bool = False) -> None:
    """Raise ``AccessDenied`` when the configured entitlement check fails."""

    decision = check_access(user, region, detail)
    if not decision.allowed:
        raise AccessDenied(decision.reason)


def allowed_regions(user: UserEntitlement) -> list[str]:
    """Expand an all-region entitlement into the four configured regions."""

    return ["NORTH", "SOUTH", "EAST", "WEST"] if "ALL" in user.regions else list(user.regions)


def filter_region(frame: pd.DataFrame, user: UserEntitlement, region: str) -> pd.DataFrame:
    """Return an authorized regional copy of a data frame."""

    enforce_access(user, region, detail=False)
    return frame.loc[frame["region"].eq(region)].copy()


def mask_identifier(value: object, suffix_length: int = 4) -> str:
    """Mask an identifier while retaining a short suffix for visual matching."""

    text = str(value)
    suffix = text[-suffix_length:] if len(text) >= suffix_length else text
    return f"••••{suffix}"

