import itertools
import operator
from typing import List

import typer
from tabulate import tabulate

from ansible_self_service.l1_entrypoints.cli import state
from ansible_self_service.l3_services.dto import AppStatus, App

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


def app_status_to_symbol(app_status: AppStatus):
    if app_status == AppStatus.UNKNOWN:
        return '?'
    elif app_status == AppStatus.INSTALLED:
        return '✓'
    elif app_status == AppStatus.UPGRADABLE:
        return '↑'
    elif app_status == AppStatus.NOT_INSTALLED:
        return '✗'
    else:
        return '?'


@app.command(name='list')
def list_apps(refresh: bool = False):  # pylint: disable=W0622
    """List all aps and their status."""
    collections = state.app_catalog_service.list_collections()
    apps_nested = [state.app_service.get_apps_for_collection(collection) for collection in collections]
    apps: List[App] = list(itertools.chain(*apps_nested))  # flatten list of lists

    if refresh:
        apps: List[App] = [state.app_service.refresh_app_state(app_to_refresh) for app_to_refresh in apps]

    table = [['Name', 'Installed', 'Collection', 'Categories']]
    table_data = [[application.name, app_status_to_symbol(application.status), application.collection.name,
                   ','.join(application.categories)]
                  for application in apps]
    table_data = sorted(table_data, key=operator.itemgetter(0))  # sort by name
    table += table_data
    typer.echo(tabulate(table, headers='firstrow'))
    # pylint: skip-file
    # TODO: run playbook with tag status to get status (not installed, installed, dysfunctional) and
    #  tag install to install
    # TODO: get updatable status by dry-running the playbook and checking for changes
    # TODO: save status and updatable in yaml state file
    # TODO: add commands to update status and upgradable
