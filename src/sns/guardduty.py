from typing import Dict, Any

from src.data.account import Account
from src.data.findings import Findings


class GuardDuty:
    Type: str = "GuardDuty Finding"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Findings:

        return Findings(
            compliance_item_type="guardduty",
            account=Account(identifier="?"),
            item="?",
            findings={"?"},
        )
