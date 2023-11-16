from abc import ABC, abstractmethod
from typing import Generic, List, Set, TypeVar
from src.data.notification import Notification

from src.data.payload import Payload

N = TypeVar("N")
P = TypeVar("P")


class Notifier(ABC, Generic[N, P]):
    @abstractmethod
    def apply_filters(self, payloads: Set[P]) -> Set[P]:  # pragma: no cover
        pass

    @abstractmethod
    def apply_mappings(self, payloads: Set[P]) -> List[N]:  # pragma: no cover
        pass

    @abstractmethod
    def send(self, notifications: List[N]) -> None:  # pragma: no cover
        pass
