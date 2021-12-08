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

    def is_not_applied(self) -> bool:
        return self.status is None

    def has_failed(self) -> bool:
        return bool(self.status and self.status.startswith("failed"))

    @property
    def reason(self) -> str:
        return self.status.removeprefix("failed: ") if self.status else ""

    @property
    def detailed_description(self) -> str:
        return f"{self.description} (details: {self.details})" if self.details else self.description
