from functools import reduce
from typing import Dict, Any

from src.config.config import Config
from src.data.account import Account
from src.data.findings import Findings


class GuardDuty:
    def __init__(self, config: Config):
        self.config = config

    Type: str = "GuardDuty Finding"

    def create_finding(self, message: Dict[str, Any]) -> Findings:
        return Findings(
            compliance_item_type="guardduty",
            account=Account(identifier=message["account"]),
            item=GuardDuty._traverse(message, "detail", "service", "action", "awsApiCallAction", "affectedResources"),
            description=message["detail"]["description"],
            findings={
                f"Type: {message['detail']['type']}",
                f"Severity: {message['detail']['severity']}",
                f"Account: {self._get_account_name(message['detail']['accountId'])} ({message['detail']['accountId']})",
                f"Team: {self._get_team_name(message['detail']['accountId'])}",
                f"Details: {GuardDuty._build_finding_url(message)}",
                f"First seen: {GuardDuty._traverse(message, 'detail', 'service', 'eventFirstSeen')}",
                f"Last seen: {GuardDuty._traverse(message, 'detail', 'service', 'eventLastSeen')}",
                f"Runbook: {self.config.get_guardduty_runbook_url()}",
            },
        )

    @staticmethod
    def _traverse(d: Dict[str, Any], *keys: str) -> str:
        return str(reduce(lambda node, key: node.get(key, {}), keys, d) or "unspecified")

    @staticmethod
    def _build_finding_url(message: Dict[str, Any]) -> str:
        return (
            f"https://{message['region']}.console.aws.amazon.com/guardduty/home?region={message['region']}#/findings?"
            f"fId={message['detail']['id']}"
        )

    def _get_account_name(self, account_id: str) -> str:
        for acc_id, acc_name in self.config.get_account_mappings().items():
            if acc_id == account_id:
                return acc_name
        return "unknown"

    def _get_team_name(self, account_id: str) -> str:
        account_name = self._get_account_name(account_id)
        for team, accounts in self.config.get_slack_mappings().items():
            if account_name in accounts:
                return team
        return "unknown"
