from ansible_self_service.core.models import AppEvent, RepoManager
from ansible_self_service.core.protocols import GuiProtocol


class Application:
    """The main application.

    Control flow start here until the GUI framework takes over.
    But even then the GUI will call functions in this class that have been registered beforehand.
    """

    def __init__(self, repo_manager: RepoManager, gui: GuiProtocol):
        self.repo_manager = repo_manager
        self.gui = gui

    def run(self):
        """Entry point of the application.

        Ititialize everything and hand over control to the GUI.
        """
        self.gui.on_event_run(AppEvent.MAIN_WINDOW_READY, self.on_main_window_ready)
        self.gui.loop()

    def on_main_window_ready(self):
        """Initialize application data right before the main window becomes visible."""
        self.repo_manager.refresh_repos()
