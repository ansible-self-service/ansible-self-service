import sys
from abc import abstractmethod
from pathlib import Path
from typing import List, Callable, Tuple, Optional, Any

from .utils import ObserverProtocol

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, TYPE_CHECKING
else:
    from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from . import models


class AppDirLocatorProtocol(Protocol):
    """Retrieve OS-specific app directories."""

    @abstractmethod
    def get_app_data_dir(self) -> Path:
        """Get the base directory that fetches and creates the directory for data files."""

    @abstractmethod
    def get_app_cache_dir(self) -> Path:
        """Get the base directory that fetches and creates the directory for cache files."""


class AppCollectionConfigParserProtocol(Protocol):
    """Parse a configuration file describing a single repo and translate it into domain object instances."""

    @abstractmethod
    def from_file(self, app_collection: 'models.AppCollection') -> Tuple[
        List['models.AppCategory'], List['models.App']]:
        """Read a repo config file, validate it and transform it into domain models."""


class AppStatePersisterProtocol(ObserverProtocol):

    def __init__(self, config: 'models.Config'):
        self._config = config

    def init_app(self, app):
        """Load state and register for  future updates from an app's state."""
        app.state = self.load(self._config.app_state_file(app))
        app.state.attach(self)

    def update(self, observable: Any, attr: str, value: Any):
        self.save(observable, self._config.app_state_file(observable))

    @abstractmethod
    def load(self, app_state_file: Path) -> 'models.AppState':
        """Retrieve an app's state."""
        raise NotImplementedError()

    @abstractmethod
    def save(self, app_state: 'models.AppState', app_state_file: Path):
        """Persist an app's state"""
        raise NotImplementedError()


class GitClientProtocol(Protocol):
    """A git client implementation."""

    @abstractmethod
    def clone_repo(self, url: str, target_dir: Path):
        """Clone a repo from a URL to a destination directory."""

    @abstractmethod
    def remove_repo(self, directory: Path):
        """Remove the git repo from the file system."""

    @abstractmethod
    def get_revision(self, directory: Path) -> str:
        """Get current revision of a git directory."""

    @abstractmethod
    def get_origin_url(self, directory: Path) -> str:
        """Get URL of the remote origin of a git directory."""

    @abstractmethod
    def list_revisions(self, directory: Path) -> List:
        """List available revisions of a git directory."""

    @abstractmethod
    def update(self, directory: Path, revision: Optional[str] = None):
        """Update the repository.

        Check out the revision if supplied else go to latest commit of origin/master or origin/main.
        """

    @abstractmethod
    def is_git_directory(self, directory: Path) -> bool:
        """True if the directory is a git repo."""


class GuiProtocol(Protocol):
    """"Represent the graphical user interface."""

    @abstractmethod
    def loop(self):
        """Take over the control flow and use registered callbacks that were defined with "on"."""

    @abstractmethod
    def show_main_window(self):
        """Show the main windows containing an overview of all items."""

    @abstractmethod
    def on_event_run(self, event: 'models.AppEvent', run: Callable, *args, **kwargs):
        """Register a callable for an event with args and kwargs."""


class AnsibleRunnerProtocol(Protocol):
    """Run ansible-playbook."""

    @abstractmethod
    def run(self, working_directory: Path, playbook_path: Path, tags=tuple(),
            check_mode: bool = False) -> 'models.AnsibleRunResult':
        """Apply a single Ansible playbook."""


class AnsibleResultAnalyzerProtocol(Protocol):
    """Extract information from an Ansible result object."""

    SIGNAL_INSTALLED: str = 'ANSIBLE_SELF_SERVICE_STATUS_INSTALLED'
    SIGNAL_NOT_INSTALLED: str = 'ANSIBLE_SELF_SERVICE_STATUS_NOT_INSTALLED'

    @abstractmethod
    def signaling_installed(self, ansible_run_result: 'models.AnsibleRunResult') -> bool:
        """Return True if the results contain ANSIBLE_SELF_SERVICE_STATUS_INSTALLED."""

    @abstractmethod
    def signaling_not_installed(self, ansible_run_result: 'models.AnsibleRunResult') -> bool:
        """Return True if the results contain ANSIBLE_SELF_SERVICE_STATUS_NOT_INSTALLED."""

    @abstractmethod
    def has_changes(self, ansible_run_result: 'models.AnsibleRunResult') -> bool:
        """Return True if the results contain at least one task with result "changed"."""
