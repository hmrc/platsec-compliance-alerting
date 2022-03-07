from dateutil import parser
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
            item="GuardDuty alert",
            description=message["detail"]["title"],
            findings={
                f"*Type:* `{message['detail']['type']}`",
                f"*Severity:* `{message['detail']['severity']}`",
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
