from dataclasses import dataclass
from typing import FrozenSet, Optional, Set

from src.data.account import Account


@dataclass(eq=True, unsafe_hash=True)
class Findings:
    account: Account
    item: str
    findings: FrozenSet[str]
    description: Optional[str]

    def __init__(
        self, account: Account, item: str, findings: Optional[Set[str]] = None, description: Optional[str] = None
    ):
        self.account = account
        self.item = item
        self.findings = frozenset(findings) if findings else frozenset()
        self.description = description
