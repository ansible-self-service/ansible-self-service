import json

import pytest

from ansible_self_service.l2_infrastructure.ansible_result_analyzer import (
    JMESPathAnsibleResultAnalyzer,
)
from ansible_self_service.l4_core.protocols import LoggerProtocol

ANSIBLE_RESULT_NOT_INSTALLED = """
{
    "custom_stats": {},
    "global_custom_stats": {},
    "plays": [
        {
            "play": {
                "duration": {
                    "end": "2022-02-23T09:53:24.386012Z",
                    "start": "2022-02-23T09:53:24.176079Z"
                },
                "id": "2b703211-0506-9b40-2d32-000000000005",
                "name": "Check Cowsay Status"
            },
            "tasks": [
                {
                    "hosts": {
                        "localhost": {
                            "_ansible_no_log": false,
                            "action": "shell",
                            "changed": true,
                            "cmd": "which cowsay",
                            "delta": "0:00:00.002330",
                            "end": "2022-02-23 10:53:24.358183",
                            "failed_when_result": false,
                            "invocation": {
                                "module_args": {
                                    "_raw_params": "which cowsay",
                                    "_uses_shell": true,
                                    "argv": null,
                                    "chdir": null,
                                    "creates": null,
                                    "executable": null,
                                    "removes": null,
                                    "stdin": null,
                                    "stdin_add_newline": true,
                                    "strip_empty_ends": true,
                                    "warn": false
                                }
                            },
                            "msg": "non-zero return code",
                            "rc": 1,
                            "start": "2022-02-23 10:53:24.355853",
                            "stderr": "",
                            "stderr_lines": [],
                            "stdout": "",
                            "stdout_lines": []
                        }
                    },
                    "task": {
                        "duration": {
                            "end": "2022-02-23T09:53:24.369417Z",
                            "start": "2022-02-23T09:53:24.184147Z"
                        },
                        "id": "2b703211-0506-9b40-2d32-000000000007",
                        "name": "Check if cowsay executable in in PATH"
                    }
                },
                {
                    "hosts": {
                        "localhost": {
                            "_ansible_no_log": false,
                            "action": "debug",
                            "changed": false,
                            "skip_reason": "Conditional result was False",
                            "skipped": true
                        }
                    },
                    "task": {
                        "duration": {
                            "end": "2022-02-23T09:53:24.377614Z",
                            "start": "2022-02-23T09:53:24.371536Z"
                        },
                        "id": "2b703211-0506-9b40-2d32-000000000008",
                        "name": "Signal status installed"
                    }
                },
                {
                    "hosts": {
                        "localhost": {
                            "_ansible_no_log": false,
                            "_ansible_verbose_always": true,
                            "action": "debug",
                            "changed": false,
                            "msg": "ANSIBLE_SELF_SERVICE_STATUS_NOT_INSTALLED"
                        }
                    },
                    "task": {
                        "duration": {
                            "end": "2022-02-23T09:53:24.386012Z",
                            "start": "2022-02-23T09:53:24.379100Z"
                        },
                        "id": "2b703211-0506-9b40-2d32-000000000009",
                        "name": "Signal status not installed"
                    }
                }
            ]
        },
        {
            "play": {
                "duration": {
                    "start": "2022-02-23T09:53:24.391386Z"
                },
                "id": "2b703211-0506-9b40-2d32-00000000000a",
                "name": "Install Cowsay"
            },
            "tasks": []
        }
    ],
    "stats": {
        "localhost": {
            "changed": 1,
            "failures": 0,
            "ignored": 0,
            "ok": 2,
            "rescued": 0,
            "skipped": 1,
            "unreachable": 0
        }
    }
}
"""

ANSIBLE_RESULT_INSTALLED = """
{
    "custom_stats": {},
    "global_custom_stats": {},
    "plays": [
        {
            "play": {
                "duration": {
                    "end": "2022-02-23T13:36:48.154701Z",
                    "start": "2022-02-23T13:36:47.962341Z"
                },
                "id": "2b703211-0506-cc3a-1ba1-000000000005",
                "name": "Check Cowsay Status"
            },
            "tasks": [
                {
                    "hosts": {
                        "localhost": {
                            "_ansible_no_log": false,
                            "action": "command",
                            "changed": false,
                            "cmd": [
                                "which",
                                "cowsay"
                            ],
                            "delta": "0:00:00.001775",
                            "end": "2022-02-23 14:36:48.126090",
                            "failed_when_result": false,
                            "invocation": {
                                "module_args": {
                                    "_raw_params": "which cowsay",
                                    "_uses_shell": false,
                                    "argv": null,
                                    "chdir": null,
                                    "creates": null,
                                    "executable": null,
                                    "removes": null,
                                    "stdin": null,
                                    "stdin_add_newline": true,
                                    "strip_empty_ends": true,
                                    "warn": false
                                }
                            },
                            "rc": 0,
                            "start": "2022-02-23 14:36:48.124315",
                            "stderr": "",
                            "stderr_lines": [],
                            "stdout": "/usr/games/cowsay",
                            "stdout_lines": [
                                "/usr/games/cowsay"
                            ]
                        }
                    },
                    "task": {
                        "duration": {
                            "end": "2022-02-23T13:36:48.138154Z",
                            "start": "2022-02-23T13:36:47.968086Z"
                        },
                        "id": "2b703211-0506-cc3a-1ba1-000000000007",
                        "name": "Check if cowsay executable in in PATH"
                    }
                },
                {
                    "hosts": {
                        "localhost": {
                            "_ansible_no_log": false,
                            "_ansible_verbose_always": true,
                            "action": "debug",
                            "changed": false,
                            "msg": "ANSIBLE_SELF_SERVICE_STATUS_INSTALLED"
                        }
                    },
                    "task": {
                        "duration": {
                            "end": "2022-02-23T13:36:48.147060Z",
                            "start": "2022-02-23T13:36:48.139926Z"
                        },
                        "id": "2b703211-0506-cc3a-1ba1-000000000008",
                        "name": "Signal status installed"
                    }
                },
                {
                    "hosts": {
                        "localhost": {
                            "_ansible_no_log": false,
                            "action": "debug",
                            "changed": false,
                            "skip_reason": "Conditional result was False",
                            "skipped": true
                        }
                    },
                    "task": {
                        "duration": {
                            "end": "2022-02-23T13:36:48.154701Z",
                            "start": "2022-02-23T13:36:48.148595Z"
                        },
                        "id": "2b703211-0506-cc3a-1ba1-000000000009",
                        "name": "Signal status not installed"
                    }
                }
            ]
        },
        {
            "play": {
                "duration": {
                    "start": "2022-02-23T13:36:48.158565Z"
                },
                "id": "2b703211-0506-cc3a-1ba1-00000000000a",
                "name": "Install Cowsay"
            },
            "tasks": []
        }
    ],
    "stats": {
        "localhost": {
            "changed": 0,
            "failures": 0,
            "ignored": 0,
            "ok": 2,
            "rescued": 0,
            "skipped": 1,
            "unreachable": 0
        }
    }
}
"""


class MockLogger(LoggerProtocol):
    def debug(self, msg: str):
        pass

    def info(self, msg: str):
        pass

    def warning(self, msg: str):
        pass

    def error(self, msg: str):
        pass


@pytest.fixture
def logger():
    return MockLogger()


def test_not_installed(mocker, logger):
    ansible_result_mock = mocker.Mock()
    ansible_result_mock.data = json.loads(ANSIBLE_RESULT_NOT_INSTALLED)
    analyzer = JMESPathAnsibleResultAnalyzer(logger)
    assert analyzer.signaling_not_installed(ansible_result_mock) is True
    assert analyzer.signaling_installed(ansible_result_mock) is False


def test_installed(mocker, logger):
    ansible_result_mock = mocker.Mock()
    ansible_result_mock.data = json.loads(ANSIBLE_RESULT_INSTALLED)
    analyzer = JMESPathAnsibleResultAnalyzer(logger)
    assert analyzer.signaling_not_installed(ansible_result_mock) is False
    assert analyzer.signaling_installed(ansible_result_mock) is True
