from dataclasses import dataclass
from typing import Set


@dataclass
class Notification:
    bucket: str
    findings: Set[str]
