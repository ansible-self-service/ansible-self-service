"""Factory classes for  complex instance creation."""
from pathlib import Path
from typing import List

from ansible_self_service.l4_core.models import App, AppCollection, AppCategory
from ansible_self_service.l4_core.protocols import (
    AnsibleRunnerProtocol,
    AppStatePersisterProtocol,
    AnsibleResultAnalyzerProtocol,
)


class AppFactory:
    def __init__(
        self,
        app_state_persister: AppStatePersisterProtocol,
        ansible_runner: AnsibleRunnerProtocol,
        ansible_result_analyzer: AnsibleResultAnalyzerProtocol,
    ):
        self._app_state_persister = app_state_persister
        self._ansible_runner = ansible_runner
        self._ansible_result_analyzer = ansible_result_analyzer

    def create_app(  # pylint: disable=too-many-arguments
        self,
        app_collection: AppCollection,
        name: str,
        description: str,
        categories: List[str],
        playbook_path: Path,
    ) -> App:
        app = App(
            app_collection=app_collection,
            name=name,
            description=description,
            categories=[AppCategory(category_name) for category_name in categories],
            playbook_path=playbook_path,
            _ansible_runner=self._ansible_runner,
            _ansible_result_analyzer=self._ansible_result_analyzer,
        )
        self._app_state_persister.init_app(app)
        return app
