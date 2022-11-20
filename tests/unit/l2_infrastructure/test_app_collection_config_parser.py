from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ansible_self_service.l2_infrastructure.app_collection_config_parser import (
    AppCollectionConfigValidationException,
    YamlAppCollectionConfigParser,
)
from ansible_self_service.l4_core.models import AppCategory

VALID_CATEGORY_NAME = "Misc"
VALID_ITEM_NAME = "Cowsay"
VALID_ITEM_DESCRIPTION = "Let an ASCII cow say stuff in your terminal!"
VALID_CONFIG = f"""
categories:
  {VALID_CATEGORY_NAME}: {{}}

items:
  {VALID_ITEM_NAME}:
    description: |
      {VALID_ITEM_DESCRIPTION}
    categories:
      - {VALID_CATEGORY_NAME}
    image_url: https://upload.wikimedia.org/wikipedia/commons/8/80/Cowsay_Typical_Output.png
    playbook: playbooks/cowsay.yml
    params:
      ansible_become_password:
        type: secret
        mandatory: true
    requirements: > # any expression that we could use for a tasks "when" clause; items are ANDed
      - ansible_distribution == 'Ubuntu'
"""

INVALID_CONFIG = """
this is not even YAML
"""


def create_app_collection(mocker, config_file):
    app_collection_mock = mocker.Mock()
    app_collection_mock.directory = Path(config_file).parent
    app_collection_mock.config = Path(config_file)
    return app_collection_mock


def create_yaml_app_collection_config_parser(mocker, tmpdir, config):
    config_file = tmpdir.join("self-service.yaml")
    config_file.write(config)
    app_stub = mocker.stub()
    ansible_runner_stub = mocker.stub()
    ansible_runner_stub.create_app = MagicMock(return_value=app_stub)
    app_collection_config_parser = YamlAppCollectionConfigParser(ansible_runner_stub)
    return config_file, ansible_runner_stub, app_stub, app_collection_config_parser


def test_parse_valid_file(tmpdir, mocker: MockerFixture):
    (
        config_file,
        ansible_runner,
        app_stub,
        app_collection_config_parser,
    ) = create_yaml_app_collection_config_parser(mocker, tmpdir, VALID_CONFIG)
    app_collection_mock = create_app_collection(mocker, config_file)
    categories, apps = app_collection_config_parser.from_file(app_collection_mock)
    assert categories == [AppCategory(name=VALID_CATEGORY_NAME)]
    assert apps == [app_stub]


def test_parse_invalid_file(tmpdir, mocker: MockerFixture):
    (
        config_file,
        ansible_runner,
        app_stub,
        repo_config_parser,
    ) = create_yaml_app_collection_config_parser(mocker, tmpdir, INVALID_CONFIG)
    with pytest.raises(AppCollectionConfigValidationException):
        app_collection_mock = mocker.Mock()
        app_collection_mock.directory = Path(config_file).parent
        app_collection_mock.config = Path(config_file)
        repo_config_parser.from_file(app_collection_mock)
