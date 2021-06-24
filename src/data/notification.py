from dataclasses import dataclass
from typing import FrozenSet, Optional, Set


@dataclass(eq=True, unsafe_hash=True)
class Notification:
    item: str
    findings: FrozenSet[str]

    def __init__(self, item: str, findings: Optional[Set[str]] = None):
        self.item = item
        self.findings = frozenset(findings) if findings else frozenset()
