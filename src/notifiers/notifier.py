from abc import ABC, abstractmethod
from typing import Set
from src.data.notification import Notification

from src.data.payload import Payload


class Notifier(ABC):
    @abstractmethod
    def apply_filters(self, payloads: Set[Payload]) -> Set[Payload]: # pragma: no cover
        pass

    @abstractmethod
    def apply_mappings(self, payloads: Set[Payload]) -> Set[Notification]: # pragma: no cover
        pass

    @abstractmethod
    def send(self, notifications: Set[Notification]) -> None: # pragma: no cover
        pass
