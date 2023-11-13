from dataclasses import dataclass
from typing import FrozenSet, Optional, Set

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
        self.item = item,
        self.severity = severity, 
        self.findings = frozenset(findings) if findings else frozenset()
        super().__init__(description=description, account=account, region_name=region_name)