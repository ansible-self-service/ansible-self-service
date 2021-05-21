from pathlib import Path
from typing import Protocol, List, Callable


class AppDirLocatorProtocol(Protocol):
    """Retrieve OS-specific app directories."""

    def get_app_data_dir(self) -> Path:
        """Get the base directory that fetches and creates the directory for data files."""

    def get_app_cache_dir(self) -> Path:
        """Get the base directory that fetches and creates the directory for cache files."""


class RepoConfigParserProtocol(Protocol):
    """Parse a configuration file describing a sinle repo and translate it into domain object instances."""

    def from_file(self, file_path) -> 'RepoConfig':
        """Read a repo config file, validate it and transform it into domain models."""


class GitClientProtocol(Protocol):
    """A git client implementation."""

    def clone_repo(self, url: str, target_dir: Path):
        """Clone a repo from a URL to a destination directory."""

    def list_revisions(self, directory: Path) -> List:
        """List available revisions of a git directory."""

    def checkout(self, revision: str, directory: Path):
        """Checkout a specific revision."""

    def is_git_directory(self, directory: Path) -> bool:
        """True if the directory is a git repo."""


class GuiProtocol(Protocol):
    """"Represent the graphical user interface."""

    def loop(self):
        """Take over the control flow and use registered callbacks that were defined with "on"."""

    def show_main_window(self):
        """Show the main windows containing an overview of all items."""

    def on_event_run(self, event: 'AppEvent', run: Callable, *args, **kwargs):
        """Register a callable for an event with args and kwargs."""


class AnsibleRunnerProtocol(Protocol):
    """Run ansible-playbook."""

    def apply(self, working_directory: str, relative_file_path: str, check_mode: bool = False) -> 'AnsibleRunResult':
        """Apply a single Ansible playbook."""
