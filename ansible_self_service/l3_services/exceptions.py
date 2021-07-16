class AppCollectionsAlreadyExistsException(Exception):
    """Raised when adding an already existing collection."""


class AppCollectionsConfigDoesNotExistException(Exception):
    """Raised when an app collection does not have a config file.."""
