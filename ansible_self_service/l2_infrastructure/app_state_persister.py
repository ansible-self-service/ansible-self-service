from pathlib import Path
from typing import Final

import yaml

from ansible_self_service.l4_core.models import AppState, AppStatus
from ansible_self_service.l4_core.protocols import AppStatePersisterProtocol

KEY_STATUS: Final[str] = 'status'


class YamlAppStatePersister(AppStatePersisterProtocol):

    def load(self, app_state_file: Path) -> AppState:
        with open(app_state_file, "r", encoding='utf-8') as stream:
            app_state_dict = yaml.safe_load(stream)
        if app_state_dict:
            status = app_state_dict[KEY_STATUS]
        else:
            status = AppStatus.UNKNOWN
        return AppState(status=status)

    def save(self, app_state: AppState, app_state_file: Path):
        with open(app_state_file, "w", encoding='utf-8') as outfile:
            yaml.dump(
                {
                    KEY_STATUS: app_state.status,
                },
                outfile,
                default_flow_style=False,
            )
