from typing import List

from ansible_self_service.l3_services.dto import AppCollection, App
from ansible_self_service.l4_core.models import AppCatalog


class AppService:
    """Provide an interface to app related features."""

    def __init__(self, app_catalog: AppCatalog):
        self._app_catalog = app_catalog

    def get_apps_for_collection(self, app_collection: AppCollection) -> List[App]:
        """Return a list of apps for a collection."""
        domain_collection = self._app_catalog.get_collection_by_name(app_collection.name)
        return [App.from_domain(app_collection, domain_app) for domain_app in domain_collection.apps.values()]

    def refresh_app_state(self, app: App) -> App:
        domain_collection = self._app_catalog.get_collection_by_name(app.collection.name)
        domain_app = domain_collection[app.name]
        domain_app.refresh_status()
        return App.from_domain(app.collection, domain_app)
