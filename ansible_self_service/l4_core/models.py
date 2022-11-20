import json
from dataclasses import dataclass, field
from enum import Enum

try:
    from functools import cached_property
except ImportError:
    cached_property = property  # type: ignore # pylint: disable=invalid-name
from pathlib import Path
from typing import List, ClassVar, Dict, Optional, Tuple

from .exceptions import (
    AppCollectionsAlreadyExistsException,
    AppCollectionsConfigDoesNotExistException,
    AppCollectionConfigValidationException,
)
from .protocols import (
    AppDirLocatorProtocol,
    GitClientProtocol,
    AppCollectionConfigParserProtocol,
    AnsibleRunnerProtocol,
    AnsibleResultAnalyzerProtocol,
)
from .utils import ObservableMixin


class AppEvent(Enum):
    """Events that may happen during the application life cycle.

    Primarily used for registering callbacks with the UI.
    """

    MAIN_WINDOW_READY = 1


class AppStatus(Enum):
    UNKNOWN = 0
    NOT_INSTALLED = 1
    INSTALLED = 2
    UPGRADABLE = 3


class AppState(ObservableMixin):
    _observed_attrs = ("status",)

    def __init__(self, status: AppStatus = AppStatus.UNKNOWN):
        super().__init__()
        self.status = status


class AppPlaybookTag(Enum):
    STATUS = "status"
    INSTALL = "install"


@dataclass
class Config:
    """ "Contains the app config."""

    def __init__(
        self,
        app_dir_locator: AppDirLocatorProtocol,
        override_app_data_dir: Optional[Path] = None,
    ):
        self.app_dir_locator = app_dir_locator
        self.app_data_dir: Path = (
            override_app_data_dir or self.app_dir_locator.get_app_data_dir()
        )

    @property
    def git_directory(self) -> Path:
        """App data directory containing all git repos with Ansible playbooks."""
        git_directory = self.app_data_dir / "git"
        git_directory.mkdir(parents=True, exist_ok=True)
        return git_directory

    def app_state_file(self, app: "App") -> Path:
        """Path to a file for saving an app's state like whether it is installed or not."""
        app_state_dir = self.app_data_dir / app.app_collection.name
        app_state_dir.mkdir(parents=True, exist_ok=True)
        app_state_file = app_state_dir / app.name
        if not app_state_file.exists():
            app_state_file.touch()
        return app_state_file


@dataclass(frozen=True)
class AnsibleRunResult:
    """Contains data about a completed Ansible run."""

    stdout: str
    stderr: str
    return_code: int

    @property
    def was_successful(self):
        """True if this run has been successful."""
        return self.return_code == 0

    @cached_property
    def data(self):
        """Parse the structured data from stdout."""
        return json.loads(self.stdout)


@dataclass(frozen=True)
class AppCategory:
    """Used for categorizing self-service items it the UI."""

    name: str


@dataclass
class App(ObservableMixin):
    """A single application that can be installed, updated or removed."""

    _ansible_runner: AnsibleRunnerProtocol
    _ansible_result_analyzer: AnsibleResultAnalyzerProtocol
    app_collection: "AppCollection"
    name: str
    description: str
    categories: List[AppCategory]
    playbook_path: Path
    state: AppState = AppState()

    def _check_upgradable(self) -> bool:
        result = self._ansible_runner.run(
            working_directory=self.app_collection.directory,
            playbook_path=self.playbook_path,
            tags=(AppPlaybookTag.INSTALL.value,),
            check_mode=True,
        )
        return self._ansible_result_analyzer.has_changes(result)

    def refresh_status(self):
        result = self._ansible_runner.run(
            working_directory=self.app_collection.directory,
            playbook_path=self.playbook_path,
            tags=(AppPlaybookTag.STATUS.value,),
            check_mode=True,
        )
        if self._ansible_result_analyzer.signaling_not_installed(result):
            self.state.status = AppStatus.NOT_INSTALLED
        elif self._ansible_result_analyzer.signaling_installed(result):
            if self._check_upgradable():
                self.state.status = AppStatus.UPGRADABLE
            else:
                self.state.status = AppStatus.INSTALLED
        else:
            self.state.status = AppStatus.UNKNOWN


@dataclass
class AppCollection:
    """A collection of apps belonging to the same repository."""

    _git_client: GitClientProtocol
    _app_collection_config_parser: AppCollectionConfigParserProtocol
    name: str
    directory: Path
    categories: Dict[str, AppCategory] = field(default_factory=dict)
    apps: Dict[str, App] = field(default_factory=dict)
    validation_error = None
    _initialized: bool = False

    CONFIG_FILE_NAME: ClassVar[str] = "self-service.yaml"

    class Decorators:
        """Nested class with decorators."""

        @classmethod
        def initialize(cls, func):
            """Decorator checking if the catalog is initialized before calling the wrapped function."""

            def wrapper(self, *args, **kwargs):
                if not self._initialized:  # pylint: disable=W0212
                    self.refresh()
                    self._initialized = True  # pylint: disable=W0212
                return func(self, *args, **kwargs)

            return wrapper

    @property
    def config(self):
        return self.directory / self.CONFIG_FILE_NAME

    def __getitem__(self, key):
        return self.apps[key]

    def refresh(self):
        """Read the repo config and (re-)initialize the collection."""
        if not self.config.exists():
            raise AppCollectionsConfigDoesNotExistException()
        try:
            categories, apps = self._app_collection_config_parser.from_file(self)
            self.categories = {category.name: category for category in categories}
            self.apps = {app.name: app for app in apps}
            self.validation_error = None
        except AppCollectionConfigValidationException as exception:
            self.categories = {}
            self.apps = {}
            self.validation_error = str(exception)

    @property  # type: ignore
    @Decorators.initialize
    def revision(self):
        """Return the current revision of the repo."""
        return self._git_client.get_revision(self.directory)

    @property  # type: ignore
    @Decorators.initialize
    def url(self):
        """Extract the remote URL from the repo."""
        return self._git_client.get_origin_url(self.directory)

    @Decorators.initialize
    def update(self, revision: Optional[str]) -> Tuple[str, str]:
        """Update the repository.

        Update to latest main/master commit if no revision is provided.
        """
        old_revision = self.revision
        self._git_client.update(directory=self.directory, revision=revision)
        new_revision = self.revision
        return old_revision, new_revision


@dataclass
class AppCatalog:
    """ "Contains all known apps."""

    _config: Config
    _git_client: GitClientProtocol
    _app_collection_config_parser: AppCollectionConfigParserProtocol
    _collections: Dict[str, AppCollection] = field(default_factory=dict)
    _initialized: bool = False

    class Decorators:
        """Nested class with decorators."""

        @classmethod
        def initialize(cls, func):
            """Decorator checking if the catalog is initialized before calling the wrapped function."""

            def wrapper(self, *args, **kwargs):
                if not self._initialized:  # pylint: disable=W0212
                    self.refresh()
                    self._initialized = True  # pylint: disable=W0212
                return func(self, *args, **kwargs)

            return wrapper

    def refresh(self):
        """Check the git directory for existing repos and add them to the list.py."""
        self._collections = {}
        for child in self._config.git_directory.iterdir():
            if self._git_client.is_git_directory(child):
                collection_name = str(child.name)
                self._collections[collection_name] = self.create_app_collection(
                    child, collection_name
                )

    def get_directory_for_collection(self, name):
        """Locate the target directory for the app repository."""
        target_dir = self._config.git_directory / name
        return target_dir

    def create_app_collection(self, directory: Path, collection_name: str):
        """Factory method for instantiating AppCollection."""
        return AppCollection(
            _git_client=self._git_client,
            _app_collection_config_parser=self._app_collection_config_parser,
            name=collection_name,
            directory=directory,
        )

    @Decorators.initialize
    def get_collection_by_name(self, name: str) -> Optional[AppCollection]:
        """Get an app by name or return none if none exists."""
        return self._collections.get(name, None)

    @Decorators.initialize
    def list(self) -> List[AppCollection]:
        """List all apps."""
        return [value for key, value in sorted(self._collections.items())]

    @Decorators.initialize
    def add(self, name: str, url: str) -> AppCollection:
        """Add an app collection."""
        target_dir = self.get_directory_for_collection(name)
        if target_dir.exists():
            raise AppCollectionsAlreadyExistsException()
        self._git_client.clone_repo(url, target_dir)
        app_collection = self.create_app_collection(target_dir, name)
        self._collections[name] = app_collection
        return app_collection

    @Decorators.initialize
    def remove(self, name):
        """Remove an app collection."""
        target_dir = self.get_directory_for_collection(name)
        if target_dir.exists():
            self._git_client.remove_repo(target_dir)
        self._collections.pop(name)
