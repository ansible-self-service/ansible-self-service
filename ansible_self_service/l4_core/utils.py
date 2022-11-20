import sys
from abc import abstractmethod
from typing import Tuple

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, Any
else:
    from typing import Protocol, Any


class ObserverProtocol(Protocol):
    @abstractmethod
    def update(self, observable: Any, attr: str, value: Any):
        raise NotImplementedError()


class ObservableMixin:
    _observed_attrs: Tuple = tuple()

    def __init__(self):
        self.__observers = set()

    def attach(self, observer: ObserverProtocol):
        self.__observers.add(observer)

    def detach(self, observer: ObserverProtocol):
        self.__observers.remove(observer)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in self._observed_attrs and hasattr(self, "__observers"):
            for observer in self.__observers:
                observer.update(observable=self, attr=key, value=value)
