import pytest

from ansible_self_service.l2_infrastructure.app_collection_config_parser import AppCollectionConfigValidationException, \
    YamlAppCollectionConfigParser
from ansible_self_service.l4_core.models import AppCategory, App

VALID_CATEGORY_NAME = 'Misc'
VALID_ITEM_NAME = 'Cowsay'
VALID_ITEM_DESCRIPTION = 'Let an ASCII cow say stuff in your terminal!'
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

INVALID_CONFIG = '''
this is not even YAML
'''


def test_parse_valid_file(tmpdir):
    config_file = tmpdir.join('self-service.yaml')
    config_file.write(VALID_CONFIG)
    repo_config_parser = YamlAppCollectionConfigParser()
    categories, apps = repo_config_parser.from_file(config_file)
    assert categories == [AppCategory(name=VALID_CATEGORY_NAME)]
    assert apps == [App(
        name=VALID_ITEM_NAME, description=VALID_ITEM_DESCRIPTION, categories=[AppCategory(name=VALID_CATEGORY_NAME)])
    ]


def test_parse_invalid_file(tmpdir):
    config_file = tmpdir.join('self-service.yaml')
    config_file.write(INVALID_CONFIG)
    repo_config_parser = YamlAppCollectionConfigParser()
    with pytest.raises(AppCollectionConfigValidationException):
        repo_config_parser.from_file(config_file)
