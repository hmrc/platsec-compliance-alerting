from dataclasses import dataclass
from typing import FrozenSet, Optional, Set

from src.data.account import Account


@dataclass(eq=True, unsafe_hash=True)
class Findings:
    compliance_item_type: str
    item: str
    findings: FrozenSet[str]
    description: Optional[str]
    account: Optional[Account] = None

    def __init__(
        self,
        compliance_item_type: str,
        item: str,
        account: Optional[Account] = None,
        findings: Optional[Set[str]] = None,
        description: Optional[str] = None,
    ):
        self.account = account
        self.compliance_item_type = compliance_item_type
        self.item = item
        self.findings = frozenset(findings) if findings else frozenset()
        self.description = description

    @property
    def account_name(self) -> str:
        return self.account.name if self.account else "unknown account"
