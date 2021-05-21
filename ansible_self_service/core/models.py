from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

from .protocols import AppDirLocatorProtocol, GitClientProtocol


class AppEvent(Enum):
    """Events that may happen during the application life cycle.

    Primarily used for registering callbacks with the UI.
    """
    MAIN_WINDOW_READY = 1


@dataclass
class Config:
    """"Contains the app config."""

    def __init__(self, app_dir_locator: AppDirLocatorProtocol):
        self.app_dir_locator = app_dir_locator

    @property
    def git_directory(self):
        """App data directory containing all git repos with Ansible playbooks."""
        git_directory = self.app_dir_locator.get_app_data_dir() / 'git'
        git_directory.mkdir(parents=True, exist_ok=True)
        return git_directory


@dataclass(frozen=True)
class AnsibleRunResult:
    """Contains data about a completed Ansible run."""
    stdout: str
    stderr: str
    return_code: int

    @property
    def was_successful(self):
        """True if this run has been successful."""
        return self.return_code != 0


@dataclass
class GitRepo:
    """"Represents a Git repository on the file system."""

    def __init__(self, path: Path, git_client: GitClientProtocol):
        self.path = path
        self._git_client = git_client

    @property
    def revision(self) -> str:
        """Current revision hash of the Git repo."""

    @property
    def directory_name(self) -> str:
        """Get the directory name of the Git repo."""
        return self.path.name


@dataclass(frozen=True)
class RepoCategory:
    """Used for categorizing self service items it the UI."""
    name: str


@dataclass(frozen=True)
class RepoApplicationItem:
    """Represents a single application that can be installed, updated or removed."""
    name: str
    description: str
    categories: List[RepoCategory]


@dataclass(frozen=True)
class RepoConfig:
    """Represents the self-service.yaml config file at the repo root.

    This file contains information about what playbooks are available to which systems.
    """
    repo_path: str
    categories: List[RepoCategory]
    items: List[RepoApplicationItem]


class RepoManager:
    """Keeps track of all cloned repos on the local file systems."""
    repos: List[GitRepo]

    def __init__(self, config: Config, git_client: GitClientProtocol):
        self._config = config
        self._git_client = git_client

    def refresh_repos(self):
        """Check the git directory for existing repos and add them to the list."""
        self.repos = []
        for child in self._config.git_directory.iterdir():
            if self._git_client.is_git_directory(child):
                self.repos.append(GitRepo(child, self._git_client))

    def add(self, url: str, name: str):  # noqa
        """Clone a git repo and add it to the list."""
        target_dir = self._config.git_directory / name
        self._git_client.clone_repo(url=url, target_dir=target_dir)
        self.repos.append(GitRepo(target_dir, git_client=self._git_client))

    def remove(self, repo: GitRepo):
        """Remove a git repo from file system and the list."""
        repo.path.unlink(missing_ok=True)
        self.repos.remove(repo)
