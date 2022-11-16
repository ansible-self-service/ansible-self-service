from typing import Optional

import typer
from giturlparse import validate  # type: ignore
from tabulate import tabulate

from . import state
from ...l3_services.exceptions import AppCollectionsAlreadyExistsException

app = typer.Typer()


@app.command()
def list():  # pylint: disable=W0622
    """List all registered app collections."""
    collections = state.app_catalog_service.list_collections()
    table = [["Name", "URL", "Config Valid", "Revision", "Directory"]]
    for collection in collections:
        config_valid = (
            "✓"
            if collection.validation_error is None
            else f"✗ ({collection.validation_error})"
        )
        table.append(
            [
                collection.name,
                collection.url,
                config_valid,
                collection.revision,
                collection.path,
            ]
        )
    typer.echo(tabulate(table, headers="firstrow"))


@app.command()
def add(url: str, name: Optional[str] = None):
    """Add a single app collection.

    If no name is provided it is derived from the last part of the URL.
    """
    if not validate(url):
        typer.echo(f"Invalid URL: {url}")
        raise typer.Exit(code=1)
    if not name:
        name = url.split("/")[-1]
        name = name.split(".")[0]
    try:
        collection = state.app_catalog_service.add(name=name, url=url)
    except AppCollectionsAlreadyExistsException:
        typer.echo(f'The app collection "{name}" already exists')
        raise typer.Exit(code=1)  # pylint: disable=W0707
    typer.echo(f'Successfully added "{name}" at revsision {collection.revision}')


@app.command()
def remove(name: str):
    """Remove an app collection.

    This does not remove existing apps."""
    state.app_catalog_service.remove(name=name)


def report_update(name, new_revision, old_revision):
    """Helper function to print information about an updated app collection."""
    if old_revision == new_revision:
        typer.echo(f"{name} is already up-to-date at revision {new_revision}")
    else:
        typer.echo(
            f"Updated {name} from revision {old_revision} to revision {new_revision}"
        )


@app.command()
def update(name: str, revision: Optional[str] = None):
    """Update an app collection."""
    old_revision, new_revision = state.app_catalog_service.update(
        name=name, revision=revision
    )
    report_update(name, new_revision, old_revision)


@app.command()
def update_all():
    """Update all app collections."""
    collections = state.app_catalog_service.list_collections()
    for collection in collections:
        old_revision, new_revision = state.app_catalog_service.update(
            name=collection.name
        )
        report_update(collection.name, new_revision, old_revision)
