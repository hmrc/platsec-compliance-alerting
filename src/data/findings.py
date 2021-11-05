from dataclasses import dataclass
from typing import FrozenSet, Optional, Set

from src.data.account import Account


@dataclass(eq=True, unsafe_hash=True)
class Findings:
    account: Account
    compliance_item_type: str
    item: str
    findings: FrozenSet[str]
    description: Optional[str]

    def __init__(
        self,
        account: Account,
        compliance_item_type: str,
        item: str,
        findings: Optional[Set[str]] = None,
        description: Optional[str] = None,
    ):
        self.account = account
        self.compliance_item_type = compliance_item_type
        self.item = item
        self.findings = frozenset(findings) if findings else frozenset()
        self.description = description
