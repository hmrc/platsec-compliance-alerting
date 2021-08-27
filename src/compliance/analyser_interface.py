from abc import ABC, abstractmethod
from src.data.audit import Audit
from src.data.notification import Notification
from typing import Set


class AnalyserInterface(ABC):
    @abstractmethod
    def analyse(self, audit: Audit) -> Set[Notification]:
        pass
