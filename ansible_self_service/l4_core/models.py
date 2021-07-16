from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, ClassVar, Dict, Optional, Tuple

from .exceptions import AppCollectionsAlreadyExistsException, AppCollectionsConfigDoesNotExistException, \
    AppCollectionConfigValidationException
from .protocols import AppDirLocatorProtocol, GitClientProtocol, AppCollectionConfigParserProtocol


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


@dataclass(frozen=True)
class AppCategory:
    """Used for categorizing self service items it the UI."""
    name: str


@dataclass(frozen=True)
class App:
    """A single application that can be installed, updated or removed."""
    name: str
    description: str
    categories: List[AppCategory]


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

    CONFIG_FILE_NAME: ClassVar[str] = 'self-service.yaml'

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
        """Read the repo config and (re-)initialize the collection."""
        config = self.directory / self.CONFIG_FILE_NAME
        if not config.exists():
            raise AppCollectionsConfigDoesNotExistException()
        try:
            categories, apps = self._app_collection_config_parser.from_file(config)
            self.categories = {category.name: category for category in categories}
            self.apps = {app.name: app for app in apps}
            self.validation_error = None
        except AppCollectionConfigValidationException as exception:
            self.categories = {}
            self.apps = {}
            self.validation_error = str(exception)

    @property # type: ignore
    @Decorators.initialize
    def revision(self):
        """Return the current revision of the repo."""
        return self._git_client.get_revision(self.directory)

    @property # type: ignore
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
    """"Contains all known apps."""
    _config: Config
    _git_client: GitClientProtocol
    _app_collection_config_parser: AppCollectionConfigParserProtocol
    _collections: dict[str, AppCollection] = field(default_factory=dict)
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
                self._collections[collection_name] = self.create_app_collection(child, collection_name)

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
            directory=directory
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
