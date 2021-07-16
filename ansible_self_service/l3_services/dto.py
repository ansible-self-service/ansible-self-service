from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
