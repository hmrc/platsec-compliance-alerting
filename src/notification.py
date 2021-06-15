from dataclasses import dataclass
from typing import FrozenSet, Optional, Set


@dataclass(eq=True, unsafe_hash=True)
class Notification:
    bucket: str
    findings: FrozenSet[str]

    def __init__(self, bucket: str, findings: Optional[Set[str]] = None):
        self.bucket = bucket
        self.findings = frozenset(findings) if findings else frozenset()
