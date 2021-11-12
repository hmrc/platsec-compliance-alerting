from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Action:
    description: str
    details: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

    @staticmethod
    def from_dict(action: Dict[str, Any]) -> Action:
        return Action(**action)

    def is_applied(self) -> bool:
        return self.status == "applied"
