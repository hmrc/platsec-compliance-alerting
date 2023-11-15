from dataclasses import dataclass
from typing import Optional
from src.data.account import Account


@dataclass
class Payload:
    description: Optional[str]
    account: Optional[Account] = None
    region_name: Optional[str] = None

    @property
    def account_name(self) -> str:
        return self.account.name if self.account else "unknown account"
