from abc import ABC, abstractmethod
from typing import Any, Dict


class Notification(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: # pragma: no cover
        pass
