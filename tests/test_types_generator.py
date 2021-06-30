from typing import Optional, Set

from src.data.account import Account
from src.data.notification import Notification


def account(identifier: str = "1234", name: str = "test-account") -> Account:
    return Account(identifier=identifier, name=name)


def notification(
    account: Account = account(), item: str = "test-item", findings: Optional[Set[str]] = None
) -> Notification:
    return Notification(account=account, item=item, findings=findings)
