from typing import List, Optional, Tuple

from ansible_self_service.l3_services.dto import AppCollection
from ansible_self_service.l3_services.exceptions import (
    AppCollectionsAlreadyExistsException,
)
from ansible_self_service.l4_core.exceptions import (
    AppCollectionsAlreadyExistsException as DomainAppCollectionsAlreadyExistsException,
)
from ansible_self_service.l4_core.models import AppCatalog


class AppCatalogService:
    """Provide an interface to app catalog related features."""

    def __init__(self, app_catalog: AppCatalog):
        self._app_catalog = app_catalog

    def add(self, name: str, url: str) -> AppCollection:
        """Add an app collection via URL."""
        try:
            collection = self._app_catalog.add(name=name, url=url)
            return AppCollection.from_domain(collection)
        except DomainAppCollectionsAlreadyExistsException as exception:
            raise AppCollectionsAlreadyExistsException() from exception

    def remove(self, name: str):
        """Add an app collection via URL."""
        self._app_catalog.remove(name=name)

    def update(self, name: str, revision: Optional[str] = None) -> Tuple[str, str]:
        """Add an app collection via URL.

        Returns a tuple (old revision, new revision).
        """
        return self._app_catalog.get_collection_by_name(name).update(revision=revision)

    def list_collections(self) -> List[AppCollection]:
        """Get a list of all collections."""
        collections = self._app_catalog.list()
        return [AppCollection.from_domain(collection) for collection in collections]
