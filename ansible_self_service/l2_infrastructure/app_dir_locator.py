from pathlib import Path

from appdirs import user_data_dir, user_cache_dir  # type: ignore

from ansible_self_service.l4_core.protocols import AppDirLocatorProtocol


class AppdirsAppDirLocatorProtocol(AppDirLocatorProtocol):
    """Implement the AppDirLocatorProtocol with the "appdirs" library."""

    APP_NAME = "ansible-self-service"

    def get_app_data_dir(self) -> Path:
        """Return a path to the user data directory."""
        return Path(user_data_dir(appname=self.APP_NAME))

    def get_app_cache_dir(self) -> Path:
        """Return a path to the user cache directory."""
        return Path(user_cache_dir(appname=self.APP_NAME))
