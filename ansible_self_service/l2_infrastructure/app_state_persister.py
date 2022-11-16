from pathlib import Path

import yaml

from ansible_self_service.l4_core.models import AppState
from ansible_self_service.l4_core.protocols import AppStatePersisterProtocol


class YamlAppStatePersister(AppStatePersisterProtocol):
    def load(self, app_state_file: Path) -> AppState:
        with open(app_state_file, "r") as stream:
            app_state_dict = yaml.safe_load(stream)
        if app_state_dict:
            status = app_state_dict["status"]
        else:
            status = AppState.status.UNKNOWN
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
