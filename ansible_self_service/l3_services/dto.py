from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from ansible_self_service.l4_core.models import App as DomainApp
from ansible_self_service.l4_core.models import AppCollection as DomainAppCollection


@dataclass(frozen=True)
class AppCollection:
    """Information about a single app collection."""

    name: str
    revision: str
    path: Path
    url: str
    validation_error: Optional[str]

    @classmethod
    def from_domain(cls, domain_app_collection: DomainAppCollection) -> 'AppCollection':
        """Parse a domain app collection and instantiate a DTO AppCollection with it."""
        return AppCollection(
            name=domain_app_collection.name,
            revision=domain_app_collection.revision,
            path=domain_app_collection.directory,
            url=domain_app_collection.url,
            validation_error=domain_app_collection.validation_error,
        )


@dataclass(frozen=True)
class App:
    """Information about a single app."""

    name: str
    categories: List[str]
    collection: AppCollection

    @classmethod
    def from_domain(cls, app_collection: AppCollection, domain_app: DomainApp) -> 'App':
        """Parse a domain app and instantiate a DTO App with it."""
        categories_sorted = [domain_category.name for domain_category in domain_app.categories]
        categories_sorted.sort()
        return App(
            name=domain_app.name,
            categories=categories_sorted,
            collection=app_collection,
        )
