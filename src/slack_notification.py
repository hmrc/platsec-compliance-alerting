from dataclasses import dataclass
from typing import FrozenSet, Set

from src.notification import Notification


@dataclass(unsafe_hash=True)
class SlackNotification:
    notification: Notification
    channels: FrozenSet[str]

    def __init__(self, notification: Notification, channels: Set[str]):
        self.notification = notification
        self.channels = frozenset(channels)
