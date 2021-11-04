import random
import string
from typing import Optional, Set, List, Dict, Any

from src.data.account import Account
from src.data.audit import Audit
from src.data.findings import Findings


def account(identifier: str = "1234", name: str = "test-account") -> Account:
    return Account(identifier=identifier, name=name)


def create_account() -> Account:
    return Account(
        identifier=str(random.randrange(100000000000, 1000000000000)),
        name=f"account-{''.join(random.choices(string.ascii_letters, k=15))}",
    )


def findings(
    account: Account = account(),
    compliance_item_type: str = "item_type",
    item: str = "test-item",
    findings: Optional[Set[str]] = None,
    description: Optional[str] = None,
) -> Findings:
    return Findings(
        account=account,
        compliance_item_type=compliance_item_type,
        item=item,
        description=description,
        findings=findings,
    )


def create_audit(report: List[Dict[str, Any]], type: str = "iam_access_keys") -> Audit:
    return Audit(type=type, report=report)

