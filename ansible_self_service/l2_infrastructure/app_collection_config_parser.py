from pathlib import Path
from typing import List, Tuple

import yaml
from cerberus.validator import Validator, DocumentError  # type: ignore

from ansible_self_service.l4_core.exceptions import AppCollectionConfigValidationException
from ansible_self_service.l4_core.models import AppCategory, App
from ansible_self_service.l4_core.protocols import AppCollectionConfigParserProtocol


class YamlAppCollectionConfigParser(AppCollectionConfigParserProtocol):
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

    def from_file(self, repo_config_file_path: Path) -> Tuple[List[AppCategory], List[App]]:
        """Read a repo config file, validate it and transform it into domain models."""
        # read
        with open('{}'.format(repo_config_file_path)) as config_file:
            config_dict = yaml.safe_load(config_file)

        # validate
        validator = Validator(self.schema)
        try:
            is_valid = validator.validate(config_dict)
        except DocumentError as err:
            raise AppCollectionConfigValidationException from err
        if not is_valid:
            raise AppCollectionConfigValidationException(validator.errors)

        # parse & return
        return self.parse(config_dict)

    def parse(self, document: dict) -> Tuple[List[AppCategory], List[App]]:
        """Parse the dict we receive from cerberus."""
        categories = [AppCategory(name=category_name) for category_name, category_data in
                      document[self.CATEGORIES].items()]
        items = [self.parse_item(item_name, item_data) for item_name, item_data in
                 document[self.ITEMS].items()]
        return categories, items

    @staticmethod
    def parse_item(item_name, item_data) -> App:
        """Parse a single application item into its domain model."""
        return App(item_name, item_data['description'].strip(),
                   [AppCategory(category_name) for category_name in item_data['categories']])
