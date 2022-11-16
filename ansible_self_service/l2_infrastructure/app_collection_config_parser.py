from pathlib import Path
from typing import List, Tuple

import yaml
from cerberus.validator import Validator, DocumentError  # type: ignore

from ansible_self_service.l4_core.exceptions import (
    AppCollectionConfigValidationException,
)
from ansible_self_service.l4_core.factories import AppFactory
from ansible_self_service.l4_core.models import AppCategory, App, AppCollection
from ansible_self_service.l4_core.protocols import AppCollectionConfigParserProtocol


class YamlAppCollectionConfigParser(AppCollectionConfigParserProtocol):
    """Parse the self-service.yaml in the repo root and translate it into domain objects."""

    CATEGORIES = "categories"
    ITEMS = "items"
    schema = {CATEGORIES: {"type": "dict"}, ITEMS: {"type": "dict"}}

    def __init__(self, app_factory: AppFactory):
        self._app_factory = app_factory

    def from_file(
        self, app_collection: AppCollection
    ) -> Tuple[List[AppCategory], List[App]]:
        """Read a repo config file, validate it and transform it into domain models."""
        # read
        with open("{}".format(app_collection.config)) as config_file:
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
        return self.parse(config_dict, app_collection)

    def parse(
        self, document: dict, app_collection: AppCollection
    ) -> Tuple[List[AppCategory], List[App]]:
        """Parse the dict we receive from cerberus."""
        categories = [
            AppCategory(name=category_name)
            for category_name, category_data in document[self.CATEGORIES].items()
        ]
        items = [
            self.parse_item(item_name, item_data, app_collection)
            for item_name, item_data in document[self.ITEMS].items()
        ]
        return categories, items

    def parse_item(self, item_name, item_data, app_collection: AppCollection) -> App:
        """Parse a single application item into its domain model."""
        return self._app_factory.create_app(
            app_collection=app_collection,
            name=item_name,
            description=item_data["description"].strip(),
            categories=item_data["categories"],
            playbook_path=self.to_absolute_path(
                app_collection.directory, Path(item_data["playbook"])
            ),
        )

    @staticmethod
    def to_absolute_path(working_dir: Path, path: Path) -> Path:
        if path.is_absolute():
            return path
        return working_dir / path
