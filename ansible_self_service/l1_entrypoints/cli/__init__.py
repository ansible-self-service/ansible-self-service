import os
import sys
from pathlib import Path
from typing import Optional

import typer
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from ansible_self_service.l1_entrypoints.cli import app, collection, state
from ansible_self_service.l2_infrastructure.ansible_result_analyzer import (
    JMESPathAnsibleResultAnalyzer,
)
from ansible_self_service.l2_infrastructure.ansible_runner import AnsibleRunner
from ansible_self_service.l2_infrastructure.app_collection_config_parser import (
    YamlAppCollectionConfigParser,
)
from ansible_self_service.l2_infrastructure.app_dir_locator import (
    AppdirsAppDirLocatorProtocol,
)
from ansible_self_service.l2_infrastructure.app_state_persister import (
    YamlAppStatePersister,
)
from ansible_self_service.l2_infrastructure.git_client import GitPythonGitClient
from ansible_self_service.l2_infrastructure.logger import BasicLogger
from ansible_self_service.l3_services.app import AppService
from ansible_self_service.l3_services.app_catalog import AppCatalogService
from ansible_self_service.l3_services.config import ConfigService
from ansible_self_service.l4_core.factories import AppFactory
from ansible_self_service.l4_core.models import AppCatalog, Config

typer_app = typer.Typer()

typer_app.add_typer(app.app, name="app")
typer_app.add_typer(collection.app, name="collection")


class Container(containers.DeclarativeContainer):
    """Dependency injection container determining how all application logic classes are instantiated."""

    cli_config = providers.Configuration()
    logger = providers.Singleton(BasicLogger)
    app_dir_locator = providers.Singleton(AppdirsAppDirLocatorProtocol)
    config = providers.Singleton(
        Config,
        app_dir_locator=app_dir_locator,
        override_app_data_dir=cli_config.with_custom_data_dir,  # pylint: disable=no-member
    )
    git_client = providers.Singleton(GitPythonGitClient)
    ansible_runner = providers.Singleton(AnsibleRunner)
    ansible_result_analyzer = providers.Singleton(
        JMESPathAnsibleResultAnalyzer,
        logger=logger,
    )
    app_state_persister = providers.Singleton(
        YamlAppStatePersister,
        config=config,
    )
    app_factory = providers.Singleton(
        AppFactory,
        app_state_persister=app_state_persister,
        ansible_runner=ansible_runner,
        ansible_result_analyzer=ansible_result_analyzer,
    )
    app_collection_config_parser = providers.Singleton(
        YamlAppCollectionConfigParser,
        app_factory=app_factory,
    )

    app_catalog = providers.Singleton(
        AppCatalog,
        _config=config,
        _git_client=git_client,
        _app_collection_config_parser=app_collection_config_parser,
    )
    config_service = providers.Singleton(
        ConfigService,
        config=config,
    )
    app_catalog_service = providers.Singleton(
        AppCatalogService,
        app_catalog=app_catalog,
    )
    app_service = providers.Singleton(
        AppService,
        app_catalog=app_catalog,
    )


@inject
def get_config_service(
    config_service: ConfigService = Provide[Container.config_service],
) -> ConfigService:
    """Let the DI framework inject an instance of ConfigService and return it."""
    return config_service


@inject
def get_app_catalog_service(
    app_catalog_service: AppCatalogService = Provide[Container.app_catalog_service],
) -> AppCatalogService:
    """Let the DI framework inject an instance of AppCatalogService and return it."""
    return app_catalog_service


@inject
def get_app_service(
    app_service: AppService = Provide[Container.app_service],
) -> AppService:
    """Let the DI framework inject an instance of AppService and return it."""
    return app_service


@typer_app.callback()
def set_state(
    ctx: typer.Context,  # pylint: disable=W0613
    data_dir: Optional[Path] = typer.Option(
        default=None,
        help="Set data directory to this location. Will be created if it does not exist.",
    ),
    chdir: Optional[Path] = typer.Option(
        default=None,
        help="Set current working directory to this path. Only needed for privilege escalation.",
    ),
):
    """This runs before each command and sets the initial application state."""
    if chdir:
        os.chdir(chdir)
    container = Container()
    container.cli_config.from_dict(
        {"with_custom_data_dir": Path(data_dir) if data_dir else None}
    )
    container.wire(modules=[sys.modules[__name__]])  # pylint: disable=E1101
    state.config_service = get_config_service()
    state.app_catalog_service = get_app_catalog_service()
    state.app_service = get_app_service()


def main():
    """CLI entrypoint."""
    typer_app()


if __name__ == "__main__":
    main()
