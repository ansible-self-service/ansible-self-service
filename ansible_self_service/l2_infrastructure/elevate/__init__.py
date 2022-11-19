import os
import sys
from pathlib import Path


def elevate(show_console=True, graphical=True, with_args=None):
    """
    Re-launch the current process with root/admin privileges
    When run as root, this function does nothing.
    When not run as root, this function replaces the current process (Linux,
    macOS) or creates a child process, waits, and exits (Windows).
    :param show_console: (Windows only) if True, show a new console for the
        child process. Ignored on Linux / macOS.
    :param graphical: (Linux / macOS only) if True, attempt to use graphical
        programs (gksudo, etc). Ignored on Windows.
    :param with_args: Set arguments to restart the process with. Defaults to sys.argv.
        If the first element contains a relative path it is converted to an absolute one.
    """
    if with_args is None:
        with_args = sys.argv
    script_path = Path(with_args[0])
    if script_path.exists() and not script_path.is_absolute():
        with_args[0] = str(script_path.resolve())
    if sys.platform.startswith("win"):
        from .windows import elevate
    else:
        from .posix import elevate
    elevate(show_console, graphical, with_args)


def is_root():
    return os.getuid() == 0
