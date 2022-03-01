from functools import reduce
from typing import Dict, Any

from src.data.account import Account
from src.data.findings import Findings


class GuardDuty:
    Type: str = "GuardDuty Finding"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Findings:
        return Findings(
            compliance_item_type="guardduty",
            account=Account(identifier=message["account"]),
            item=GuardDuty._traverse(message, "detail", "service", "action", "awsApiCallAction", "affectedResources"),
            description=message["detail"]["description"],
            findings={message["detail"]["type"]},
        )

    @staticmethod
    def _traverse(d: Dict[str, Any], *keys: str) -> str:
        return str(reduce(lambda node, key: node.get(key, {}), keys, d) or "unknown")
