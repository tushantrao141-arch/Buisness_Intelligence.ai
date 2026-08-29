"""Configuration loading and cross-file validation."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from src.schemas import (
    ActionCollection,
    ConfigBundle,
    KPICollection,
    Settings,
    UserCollection,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ConfigurationError(RuntimeError):
    """Raised when a required configuration file cannot be loaded."""


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigurationError(f"Missing required configuration file: {path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigurationError(f"Expected a YAML mapping in {path}")
    return data


@lru_cache(maxsize=4)
def load_config_bundle(project_root: str | Path | None = None) -> ConfigBundle:
    """Load all governed configuration and validate cross-file references."""

    root = Path(project_root).resolve() if project_root else PROJECT_ROOT
    config_dir = root / "configs"

    settings = Settings.model_validate(_read_yaml(config_dir / "settings.yaml"))
    kpi_collection = KPICollection.model_validate(
        _read_yaml(config_dir / "kpi_contracts.yaml")
    )
    action_collection = ActionCollection.model_validate(
        _read_yaml(config_dir / "action_playbooks.yaml")
    )
    user_collection = UserCollection.model_validate(
        _read_yaml(config_dir / "users.yaml")
    )

    return ConfigBundle(
        settings=settings,
        kpis=tuple(kpi_collection.kpis),
        actions=tuple(action_collection.actions),
        users=tuple(user_collection.users),
    )


def get_user(user_id: str, bundle: ConfigBundle | None = None):
    """Return a configured user or raise a clear lookup error."""

    active_bundle = bundle or load_config_bundle()
    for user in active_bundle.users:
        if user.id == user_id:
            return user
    raise KeyError(f"Unknown configured user: {user_id}")


def get_kpi(kpi_id: str, bundle: ConfigBundle | None = None):
    """Return a configured KPI contract or raise a clear lookup error."""

    active_bundle = bundle or load_config_bundle()
    for kpi in active_bundle.kpis:
        if kpi.id == kpi_id:
            return kpi
    raise KeyError(f"Unknown configured KPI: {kpi_id}")

