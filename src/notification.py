from dataclasses import dataclass
from typing import FrozenSet, Set


@dataclass(eq=True, unsafe_hash=True)
class Notification:
    bucket: str
    findings: FrozenSet[str]

    def __init__(self, bucket: str, findings: Set[str]):
        self.bucket = bucket
        self.findings = frozenset(findings)
