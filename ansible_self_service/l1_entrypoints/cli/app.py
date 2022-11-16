import itertools
import operator

import typer
from tabulate import tabulate

from ansible_self_service.l1_entrypoints.cli import state

app = typer.Typer()


@app.command()
def install(app_name: str, collection: str = None):
    """Install an app via Ansible."""


@app.command()
def update():
    """Reinstall and app via Ansible and update it in the process."""


@app.command()
def uninstall():
    """Remove an app from the system."""


@app.command(name="list")
def list_apps():  # pylint: disable=W0622
    """List all aps and their status."""
    collections = state.app_catalog_service.list_collections()
    apps_nested = [
        state.app_service.get_apps_for_collection(collection)
        for collection in collections
    ]
    apps = list(itertools.chain(*apps_nested))  # flatten list of lists

    table = [["Name", "Collection", "Categories"]]
    table_data = [
        [
            application.name,
            application.collection.name,
            ",".join(application.categories),
        ]
        for application in apps
    ]
    table_data = sorted(table_data, key=operator.itemgetter(0))  # sort by name
    table += table_data
    typer.echo(tabulate(table, headers="firstrow"))  #
    # pylint: skip-file
    # TODO: run playbook with tag status to get status (not installed, installed, dysfunctional) and
    #  tag install to install
    # TODO: get updatable status by dry-running the playbook and checking for changes
    # TODO: save status and updatable in yaml state file
    # TODO: add commands to update status and upgradable
