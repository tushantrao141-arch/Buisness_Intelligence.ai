"""Run lightweight validation without starting Streamlit."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config_bundle  # noqa: E402


def main() -> None:
    bundle = load_config_bundle(PROJECT_ROOT)
    summary = {
        "project": bundle.settings.project.name,
        "version": bundle.settings.project.version,
        "kpi_count": len(bundle.kpis),
        "action_count": len(bundle.actions),
        "user_count": len(bundle.users),
        "llm_enabled": bundle.settings.llm.enabled,
        "synthetic_data_only": bundle.settings.project.synthetic_data_only,
        "raw_identifiers_to_llm": (
            bundle.settings.security.send_raw_identifiers_to_llm
        ),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
