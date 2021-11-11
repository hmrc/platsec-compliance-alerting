from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Action:
    description: str
    details: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
