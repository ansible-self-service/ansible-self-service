import os
from contextlib import contextmanager
from pathlib import Path

from ansible import context
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

from ansible_self_service.l4_core.models import AnsibleRunResult
from ansible_self_service.l4_core.protocols import AnsibleRunnerProtocol


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


class AnsibleRunner(AnsibleRunnerProtocol):
    """Run ansible-playbook."""

    def run(
        self,
        working_directory: Path,
        playbook_path: Path,
        tags=tuple(),
        check_mode: bool = False,
    ) -> AnsibleRunResult:
        sources = "localhost,"
        context.CLIARGS = ImmutableDict(
            connection="smart",
            module_path=[],
            forks=10,
            become=None,
            tags=tags,
            become_method=None,
            become_user=None,
            check=check_mode,
            diff=True,
        )
        loader = DataLoader()
        passwords: dict[str, str] = {}
        inventory = InventoryManager(loader=loader, sources=sources)
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        pbex = PlaybookExecutor(
            playbooks=[playbook_path],
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=passwords,
        )
        with set_directory(working_directory):
            pbex.run()
        return AnsibleRunResult("", "", 0)
