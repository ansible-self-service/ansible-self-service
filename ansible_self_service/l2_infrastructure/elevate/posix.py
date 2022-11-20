import errno
import os
import sys

try:
    from shlex import quote
except ImportError:
    from pipes import quote


def quote_shell(args):
    return " ".join(quote(arg) for arg in args)


def quote_applescript(string):
    charmap = {
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        '"': '\\"',
        "\\": "\\\\",
    }
    return f'"{"".join(charmap.get(char, char) for char in string)}"'


def elevate(_=True, graphical=True, with_args=None):
    if with_args is None:
        with_args = sys.argv
    if os.getuid() == 0:
        return

    args = [sys.executable] + with_args
    commands = []

    if graphical:
        if sys.platform.startswith("darwin"):
            commands.append(
                [
                    "osascript",
                    "-e",
                    f"do shell script {quote_applescript(quote_shell(args))} "
                    "with administrator privileges "
                    "without altering line endings",
                ]
            )

        if sys.platform.startswith("linux") and os.environ.get("DISPLAY"):
            commands.append(["pkexec"] + args)
            commands.append(["gksudo"] + args)
            commands.append(["kdesudo"] + args)

    commands.append(["sudo"] + args)

    for args in commands:
        try:
            os.execlp(args[0], *args)
        except OSError as err:
            if err.errno != errno.ENOENT or args[0] == "sudo":
                raise
