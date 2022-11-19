import io
import os
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from pathlib import Path

from ansible_self_service.l2_infrastructure.utils import processify, set_env
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

    @staticmethod
    def __clear_ansible_env_vars():
        """Unset ANSIBLE_XXX env vars, so they do not interfere with our run."""
        for env_var in os.environ:
            if env_var.startswith("ANSIBLE_"):
                del os.environ[env_var]

    @processify
    def run(
        self,
        working_directory: Path,
        playbook_path: Path,
        tags=tuple(),
        check_mode: bool = False,
    ) -> AnsibleRunResult:
        """Run a single Ansible playbook.

        Since Ansible initializes global state (ansible.constants) on import it is crucial to run this function in an
        own process e.g. via multiprocessing. Then the import does not affect the main process and Ansible runs happen
        in isolation.
        """
        self.__clear_ansible_env_vars()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with set_env(ANSIBLE_STDOUT_CALLBACK="ansible.posix.json"):
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    with set_directory(working_directory):
                        from ansible.cli.playbook import PlaybookCLI

                        args = ["ansible-playbook", str(playbook_path)]
                        if len(tags) > 0:
                            args += ["--tags", ",".join(tags)]
                        if check_mode:
                            args.append("--check")
                        cli = PlaybookCLI(args)
                        result = cli.run()
        return AnsibleRunResult(stdout.getvalue(), stderr.getvalue(), result)
