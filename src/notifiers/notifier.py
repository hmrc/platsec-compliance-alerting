from abc import ABC, abstractmethod
from typing import Generic, List, Set, TypeVar

N = TypeVar("N")
P = TypeVar("P")


class Notifier(ABC, Generic[N, P]):
    @abstractmethod
    def apply_filters(self, payloads: Set[P]) -> Set[P]:
        pass

    @abstractmethod
    def apply_mappings(self, payloads: Set[P]) -> List[N]:
        pass

    @abstractmethod
    def send(self, notifications: List[N]) -> None:
        pass
