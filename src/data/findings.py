from dataclasses import dataclass
from typing import FrozenSet, Optional, Set

from src.data.account import Account
from src.data.severity import Severity


@dataclass(eq=True, unsafe_hash=True)
class Findings:
    severity: Severity
    compliance_item_type: str
    item: str
    findings: FrozenSet[str]
    description: Optional[str]
    account: Optional[Account] = None
    region_name: Optional[str] = None

    def __init__(
        self,
        compliance_item_type: str,
        item: str,
        severity: Severity = Severity.HIGH,
        region_name: Optional[str] = None,
        account: Optional[Account] = None,
        findings: Optional[Set[str]] = None,
        description: Optional[str] = None,
    ):
        self.region_name = region_name
        self.severity = severity
        self.account = account
        self.compliance_item_type = compliance_item_type
        self.item = item
        self.findings = frozenset(findings) if findings else frozenset()
        self.description = description

    @property
    def account_name(self) -> str:
        return self.account.name if self.account else "unknown account"
