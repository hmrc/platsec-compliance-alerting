from abc import ABC, abstractmethod
from typing import Set
from src.data.notification import Notification

from src.data.payload import Payload


class Notifier(ABC):
    @abstractmethod
    def apply_filters(self, payloads: Set[Payload]) -> Set[Payload]:
        pass

    @abstractmethod
    def apply_mappings(self, payloads: Set[Payload]) -> Set[Notification]:
        pass

    @abstractmethod
    def send(self, notifications: Set[Notification]) -> None:
        pass
