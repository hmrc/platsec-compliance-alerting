import random
import string
from typing import Optional, Set, List, Dict, Any

from src.data.account import Account
from src.data.audit import Audit
from src.data.findings import Findings
from src.data.severity import Severity


def account(identifier: str = "1234", name: str = "test-account") -> Account:
    return Account(identifier=identifier, name=name)


def create_account() -> Account:
    return Account(
        identifier=str(random.randrange(100000000000, 1000000000000)),
        name=f"account-{''.join(random.choices(string.ascii_letters, k=15))}",
    )


def findings(
    severity: Severity = Severity.HIGH,
    account: Optional[Account] = account(),
    compliance_item_type: str = "item_type",
    item: str = "test-item",
    region_name: Optional[str] = "test-region-name",
    findings: Optional[Set[str]] = None,
    description: Optional[str] = None,
) -> Findings:
    return Findings(
        severity=severity,
        account=account,
        region_name=region_name,
        compliance_item_type=compliance_item_type,
        item=item,
        description=description,
        findings=findings,
    )


def create_audit(report: List[Dict[str, Any]], type: str = "iam_access_keys") -> Audit:
    return Audit(type=type, report=report)
