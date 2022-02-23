from pathlib import Path

from ansible_self_service.l4_core.models import Config


class ConfigService:
    """Provide an interface to app catalog related features."""

    def __init__(self, config: Config):
        self._config = config

    def get_app_data_dir(self) -> Path:
        return self._config.app_data_dir
