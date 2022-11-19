from pathlib import Path
from typing import Dict

import yaml

from ansible_self_service.l4_core.models import AppState, AppStatus
from ansible_self_service.l4_core.protocols import AppStatePersisterProtocol


class YamlAppStatePersister(AppStatePersisterProtocol):
    def load(self, app_state_file_path: Path) -> AppState:
        with open(app_state_file_path, "r") as app_state_file:
            app_state_dict: Dict = yaml.safe_load(app_state_file) or {}
        status = app_state_dict.get("status", AppStatus.UNKNOWN)
        return AppState(status=status)

    def save(self, app_state: AppState, app_state_file: Path):
        with open(app_state_file, "w") as outfile:
            yaml.dump(
                {
                    "status": app_state.status,
                },
                outfile,
                default_flow_style=False,
            )
