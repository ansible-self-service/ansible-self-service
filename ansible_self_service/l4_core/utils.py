from abc import abstractmethod
from typing import Protocol, Any, Tuple, Set
from dataclasses import dataclass, field


class ObserverProtocol(Protocol):
    @abstractmethod
    def update(self, observable: Any, attr: str, value: Any):
        raise NotImplementedError()


@dataclass
class ObservableMixin:
    _observed_attrs: Tuple = field(default_factory=tuple, init=False)
    __observers: Set = field(default_factory=set, init=False)

    def attach(self, observer: ObserverProtocol):
        self.__observers.add(observer)

    def detach(self, observer: ObserverProtocol):
        self.__observers.remove(observer)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in self._observed_attrs:
            [
                observer.update(observable=self, attr=key, value=value)
                for observer in self.__observers
            ]
