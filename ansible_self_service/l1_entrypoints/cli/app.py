import itertools
import operator
import os
import sys
import time
from typing import List

import click_spinner
import typer
from tabulate import tabulate

from ansible_self_service.l1_entrypoints.cli import state
from ansible_self_service.l2_infrastructure.elevate import elevate, is_root
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


def elevate_with_current_data_dir():
    """Rerun process with privileged user.

    Keep the same data directory by providing it via CLI argument.
    """
    position_of_this_subcommand = sys.argv.index('app')
    args = sys.argv[:position_of_this_subcommand] + \
           ['--data-dir', str(state.config_service.get_app_data_dir())] + \
           ['--chdir', os.getcwd()] + \
           sys.argv[position_of_this_subcommand:]
    elevate(with_args=args)


@app.command(name='list')
def list_apps(refresh: bool = False):  # pylint: disable=W0622
    """List all aps and their status."""
    collections = state.app_catalog_service.list_collections()
    apps_nested = [state.app_service.get_apps_for_collection(collection) for collection in collections]
    apps: List[App] = list(itertools.chain(*apps_nested))  # flatten list of lists

    if refresh:
        # refreshing app state requires root for ansible dry runs
        #if not is_root():
        #    typer.echo('🚀 Elevating privileges for app refresh...')
        #    elevate_with_current_data_dir()
        typer.echo('⟳  Refreshing app state...')
        with click_spinner.spinner():
            apps: List[App] = [state.app_service.refresh_app_state(app_to_refresh) for app_to_refresh in apps]
        typer.echo("\r ")

    table = [['Name', 'Status', 'Collection', 'Categories']]
    table_data = [[application.name, app_status_to_symbol(application.status), application.collection.name,
                   ','.join(application.categories)]
                  for application in apps]
    table_data = sorted(table_data, key=operator.itemgetter(0))  # sort by name
    table += table_data
    typer.echo(tabulate(table, headers='firstrow'))
    typer.echo('')
    typer.echo(f"{app_status_to_symbol(AppStatus.INSTALLED)} installed, "
               f"{app_status_to_symbol(AppStatus.UPGRADABLE)} can be upgraded, "
               f"{app_status_to_symbol(AppStatus.NOT_INSTALLED)} not installed, "
               f"{app_status_to_symbol(AppStatus.UNKNOWN)} unknown")
    # pylint: skip-file
    # TODO: run playbook with tag status to get status (not installed, installed, dysfunctional) and
    #  tag install to install
    # TODO: get updatable status by dry-running the playbook and checking for changes
    # TODO: save status and updatable in yaml state file
    # TODO: add commands to update status and upgradable
