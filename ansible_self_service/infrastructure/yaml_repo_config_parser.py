from pathlib import Path

import yaml
from cerberus.validator import Validator, DocumentError

from ansible_self_service.core.models import RepoConfig, RepoCategory, RepoApplicationItem


class YamlRepoConfigParser:
    """Parse the self-service.yaml in the repo root and translate it into domain objects."""
    CATEGORIES = 'categories'
    ITEMS = 'items'
    schema = {
        CATEGORIES: {
            'type': 'dict'
        },
        ITEMS: {
            'type': 'dict'
        }
    }

    def from_file(self, repo_config_file_path: Path) -> RepoConfig:
        """Read a repo config file, validate it and transform it into domain models."""
        # read
        with open('{}'.format(repo_config_file_path)) as config_file:
            config_dict = yaml.safe_load(config_file)

        # validate
        validator = Validator(self.schema)
        try:
            is_valid = validator.validate(config_dict)
        except DocumentError as err:
            raise RepoConfigValidationException from err
        if not is_valid:
            raise RepoConfigValidationException(validator.errors)

        # parse & return
        return self.parse(config_dict, repo_config_file_path)

    def parse(self, document: dict, repo_config_file_path) -> RepoConfig:
        """Parse the dict we receive from cerberus."""
        categories = [RepoCategory(name=category_name) for category_name, category_data in
                      document[self.CATEGORIES].items()]
        items = [self.parse_item(item_name, item_data) for item_name, item_data in
                 document[self.ITEMS].items()]
        repo_config = RepoConfig(repo_config_file_path, categories=categories, items=items)
        return repo_config

    @staticmethod
    def parse_item(item_name, item_data):
        """Parse a single application item into its domain model."""
        return RepoApplicationItem(item_name, item_data['description'].strip(),
                                   [RepoCategory(category_name) for category_name in item_data['categories']])


class RepoConfigValidationException(Exception):
    """Raised when the the config file is invalid."""
