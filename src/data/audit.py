from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Audit:
    type: str
    report: List[Dict[str, Any]]
