import jmespath

from ansible_self_service.l4_core import models  # pylint: disable=unused-import
from ansible_self_service.l4_core.protocols import AnsibleResultAnalyzerProtocol


class JMESPathAnsibleResultAnalyzer(AnsibleResultAnalyzerProtocol):
    JMESPATH_QUERY_NUMBER_OF_TASKS_CONTAINING_MESSAGE = (
        "length(plays[].tasks[?hosts.localhost.msg=='{msg}'][])"
    )

    def _get_number_of_tasks_with_message(self, msg: str, data: dict):
        query = self.JMESPATH_QUERY_NUMBER_OF_TASKS_CONTAINING_MESSAGE.format(msg=msg)
        return jmespath.search(query, data)

    def signaling_installed(
        self, ansible_run_result: "models.AnsibleRunResult"
    ) -> bool:
        tasks_with_installed_msg = self._get_number_of_tasks_with_message(
            self.SIGNAL_INSTALLED, ansible_run_result.data
        )
        return tasks_with_installed_msg > 0

    def signaling_not_installed(
        self, ansible_run_result: "models.AnsibleRunResult"
    ) -> bool:
        tasks_with_not_installed_msg = self._get_number_of_tasks_with_message(
            self.SIGNAL_NOT_INSTALLED, ansible_run_result.data
        )
        return tasks_with_not_installed_msg > 0

    def has_changes(self, ansible_run_result: "models.AnsibleRunResult") -> bool:
        try:
            return (
                int(jmespath.search("stats.localhost.changed", ansible_run_result.data))
                > 0
            )
        except TypeError:
            # TODO: log error
            return False
