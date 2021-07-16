import typer

app = typer.Typer()


@app.command()
def install():
    """Install an app via Ansible."""


@app.command()
def update():
    """Reinstall and app via Ansible and update it in the process."""


@app.command()
def uninstall():
    """Remove an app from the system."""


@app.command()
def list():  # pylint: disable=W0622
    """List all aps and their status."""
