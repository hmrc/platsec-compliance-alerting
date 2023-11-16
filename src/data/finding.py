from dataclasses import dataclass
from typing import Optional, Set

from src.data.account import Account
from src.data.payload import Payload
from src.data.severity import Severity


@dataclass(eq=True, unsafe_hash=True)
class Finding(Payload):
    def __init__(
        self,
        compliance_item_type: str,
        item: str,
        findings: Optional[Set[str]] = None,
        severity: Severity = Severity.HIGH,
        description: Optional[str] = None,
        account: Optional[Account] = None,
        region_name: Optional[str] = None,
    ):
        self.compliance_item_type = compliance_item_type
        self.item = item
        self.severity = severity
        self.findings = frozenset(findings) if findings else frozenset()
        super().__init__(description=description, account=account, region_name=region_name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Finding):
            return (
                self.compliance_item_type == other.compliance_item_type
                and self.item == other.item
                and self.findings == other.findings
                and self.severity == other.severity
                and self.description == other.description
                and self.account == other.account
                and self.region_name == other.region_name
            )
        return False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"compliance_item_type={self.compliance_item_type}, "
            f"item={self.item}, "
            f"findings={self.findings}, "
            f"severity={self.severity}, "
            f"description={self.description}, "
            f"account={self.account}, "
            f"region_name={self.region_name}"
            ")"
        )
