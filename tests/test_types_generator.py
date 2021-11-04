from typing import Optional, Set

from src.data.account import Account
from src.data.findings import Findings


def account(identifier: str = "1234", name: str = "test-account") -> Account:
    return Account(identifier=identifier, name=name)


def findings(account: Account = account(), item: str = "test-item", findings: Optional[Set[str]] = None) -> Findings:
    return Findings(account=account, item=item, findings=findings)
