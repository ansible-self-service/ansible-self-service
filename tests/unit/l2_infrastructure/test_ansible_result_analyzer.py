import json

from ansible_self_service.l2_infrastructure.ansible_result_analyzer import JMESPathAnsibleResultAnalyzer

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


def test_not_installed(mocker):
    ansible_result_mock = mocker.Mock()
    ansible_result_mock.data = json.loads(ANSIBLE_RESULT_NOT_INSTALLED)
    analyzer = JMESPathAnsibleResultAnalyzer()
    assert analyzer.signaling_not_installed(ansible_result_mock) is True
    assert analyzer.signaling_installed(ansible_result_mock) is False
