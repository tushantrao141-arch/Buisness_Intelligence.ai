"""Validated configuration schemas for SilentSignal.

These models define the contracts that later analytical modules must obey.
Keeping them independent from Streamlit lets tests validate the project without
starting the user interface.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Region = Literal["ALL", "NORTH", "SOUTH", "EAST", "WEST"]
Role = Literal["compliance_head", "regional_investigator"]


class StrictModel(BaseModel):
    """Base model that rejects unknown configuration keys."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ProjectInfo(StrictModel):
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    currency: Literal["INR"]
    timezone: Literal["UTC"]
    synthetic_data_only: bool


class AnalysisSettings(StrictModel):
    illustrative_threshold_inr: float = Field(gt=0)
    near_threshold_lower_ratio: float = Field(gt=0, lt=1)
    movement_history_days: int = Field(ge=7)
    sparse_history_days: int = Field(ge=7)
    sla_risk_horizon_hours: int = Field(gt=0)
    abstention_confidence_below: float = Field(ge=0, le=1)
    review_score_threshold: float = Field(ge=0, le=100)
    connected_pattern_minimum_near_events: int = Field(ge=1)
    connected_pattern_minimum_account_coverage: float = Field(gt=0, le=1)


class FreshnessSettings(StrictModel):
    transactions: float = Field(gt=0)
    kyc: float = Field(gt=0)
    cases: float = Field(gt=0)


class SourceContract(StrictModel):
    display_name: str = Field(min_length=2)
    grain: str = Field(min_length=5)
    refresh_cadence: str = Field(min_length=5)


class SourceContracts(StrictModel):
    transactions: SourceContract
    kyc: SourceContract
    cases: SourceContract


class SecuritySettings(StrictModel):
    mask_account_suffix_length: int = Field(ge=2, le=8)
    send_raw_identifiers_to_llm: Literal[False]


class LLMSettings(StrictModel):
    enabled: bool
    provider: Literal["openai"]
    model: str = Field(min_length=1)
    structured_output: bool
    deterministic_fallback: bool


class Settings(StrictModel):
    project: ProjectInfo
    analysis: AnalysisSettings
    freshness_sla_hours: FreshnessSettings
    source_contracts: SourceContracts
    security: SecuritySettings
    llm: LLMSettings


class AccessPolicy(StrictModel):
    aggregate_roles: list[Role] = Field(min_length=1)
    detail_roles: list[Role]


class MaterialityRule(StrictModel):
    delta_mode: Literal["absolute", "increase"]
    delta_threshold: float = Field(ge=0)
    delta_comparison: Literal["gte", "gt"] = "gte"
    z_score_mode: Literal["absolute", "increase"]
    z_score_threshold: float = Field(ge=0)
    z_score_comparison: Literal["gte", "gt"] = "gte"
    combination: Literal["and", "or"]


class KPIContract(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=3)
    description: str = Field(min_length=10)
    formula: str = Field(min_length=10)
    unit: Literal["percent", "INR", "count"]
    grain: Literal["region_day", "region_week", "region_hour"]
    owner: str = Field(min_length=2)
    sources: list[Literal["transactions", "kyc", "cases"]] = Field(min_length=1)
    drivers: list[str] = Field(min_length=1)
    calculation_notes: list[str] = Field(min_length=1)
    lineage: list[str] = Field(min_length=2)
    refresh_sla_hours: float = Field(gt=0)
    minimum_history_days: int = Field(ge=1)
    materiality: MaterialityRule
    access: AccessPolicy


class KPICollection(StrictModel):
    kpis: list[KPIContract] = Field(min_length=1)

    @model_validator(mode="after")
    def ensure_unique_ids(self) -> "KPICollection":
        ids = [kpi.id for kpi in self.kpis]
        if len(ids) != len(set(ids)):
            raise ValueError("KPI IDs must be unique")
        return self


class ActionPlaybook(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    trigger_driver: str = Field(min_length=2)
    lever: str = Field(min_length=2)
    action: str = Field(min_length=10)
    owner: str = Field(min_length=2)
    allowed_roles: list[Role] = Field(min_length=1)
    expected_impact_method: str = Field(min_length=2)
    monitoring_kpi: str = Field(min_length=2)


class ActionCollection(StrictModel):
    actions: list[ActionPlaybook] = Field(min_length=1)

    @model_validator(mode="after")
    def ensure_unique_ids(self) -> "ActionCollection":
        ids = [action.id for action in self.actions]
        if len(ids) != len(set(ids)):
            raise ValueError("Action IDs must be unique")
        return self


class UserEntitlement(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    display_name: str = Field(min_length=3)
    role: Role
    regions: list[Region] = Field(min_length=1)
    can_view_entity_detail: bool
    permitted_actions: list[str]

    @model_validator(mode="after")
    def ensure_all_region_is_exclusive(self) -> "UserEntitlement":
        if "ALL" in self.regions and len(self.regions) != 1:
            raise ValueError("ALL cannot be combined with individual regions")
        return self


class UserCollection(StrictModel):
    users: list[UserEntitlement] = Field(min_length=2)

    @model_validator(mode="after")
    def ensure_unique_ids(self) -> "UserCollection":
        ids = [user.id for user in self.users]
        if len(ids) != len(set(ids)):
            raise ValueError("User IDs must be unique")
        return self


class ConfigBundle(StrictModel):
    settings: Settings
    kpis: tuple[KPIContract, ...]
    actions: tuple[ActionPlaybook, ...]
    users: tuple[UserEntitlement, ...]

    @model_validator(mode="after")
    def validate_cross_references(self) -> "ConfigBundle":
        kpi_ids = {kpi.id for kpi in self.kpis}
        action_ids = {action.id for action in self.actions}

        unknown_monitoring = {
            action.monitoring_kpi
            for action in self.actions
            if action.monitoring_kpi not in kpi_ids
        }
        if unknown_monitoring:
            raise ValueError(
                f"Actions reference unknown monitoring KPIs: {sorted(unknown_monitoring)}"
            )

        unknown_user_actions = {
            action_id
            for user in self.users
            for action_id in user.permitted_actions
            if action_id not in action_ids
        }
        if unknown_user_actions:
            raise ValueError(
                f"Users reference unknown actions: {sorted(unknown_user_actions)}"
            )
        return self

