from dateutil import parser
from functools import reduce
from typing import Dict, Any

from src.config.config import Config
from src.data.findings import Findings


class GuardDuty:
    def __init__(self, config: Config):
        self.config = config
        self.org = config.get_org_client()

    Type: str = "GuardDuty Finding"

    def create_finding(self, message: Dict[str, Any]) -> Findings:
        account = self.org.get_account_details(message["detail"]["accountId"])

        return Findings(
            compliance_item_type="guardduty",
            account=account,
            item="GuardDuty alert",
            description=message["detail"]["title"],
            findings={
                f"*Type:* `{message['detail']['type']}`",
                f"*Severity:* `{message['detail']['severity']}`",
                f"*Team:* {self._get_team_name(account.name)}",
                f"*Links:* {self._build_links(message)}",
                f"*Timestamp:* {parser.parse(GuardDuty._traverse(message, 'detail', 'service', 'eventLastSeen'))}",
            },
        )

    @staticmethod
    def _traverse(d: Dict[str, Any], *keys: str) -> str:
        return str(reduce(lambda node, key: node.get(key, {}), keys, d) or "unspecified")

    def _build_links(self, message: Dict[str, Any]) -> str:
        gd_link = (
            f"https://{message['region']}.console.aws.amazon.com/guardduty/home?region={message['region']}#/findings?"
            f"fId={message['detail']['id']}"
        )
        runbook_link = self.config.get_guardduty_runbook_url()
        return f"<{gd_link}|GuardDuty Console> | <{runbook_link}|Runbook>"

    def _get_team_name(self, account_name: str) -> str:
        for team, accounts in self.config.get_slack_mappings().items():
            if account_name in accounts:
                return team
        return "unknown"
