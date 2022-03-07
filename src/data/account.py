from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Account:
    identifier: str
    name: str = ""
    slack_handle: str = ""

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Account):
            return NotImplemented
        return self.identifier == other.identifier

    @staticmethod
    def from_dict(account: Dict[str, str]) -> Account:
        return Account(**account)
