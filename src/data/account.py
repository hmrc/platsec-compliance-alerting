from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass(unsafe_hash=True)
class Account:
    identifier: str
    name: str

    @staticmethod
    def from_dict(account: Dict[str, str]) -> Account:
        return Account(**account)
