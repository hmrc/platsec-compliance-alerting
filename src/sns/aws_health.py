from typing import Set, Dict, Any

from src.data.account import Account
from src.data.finding import Finding
from src.data.pagerduty_payload import PagerDutyPayload

RUNBOOK = "https://confluence.tools.tax.service.gov.uk/display/SEC/Compromised+Credentials+Runbook"
EVENT_TYPE_CODES = [
    "AWS_RISK_ACCOUNT_CONSOLE_COMPROMISE",
    "AWS_RISK_CREDENTIALS_COMPROMISED",
    "AWS_RISK_CREDENTIALS_COMPROMISE_SUSPECTED",
    "AWS_RISK_CREDENTIALS_EXPOSED",
    "AWS_RISK_CREDENTIALS_EXPOSURE_SUSPECTED",
    "AWS_RISK_IAM_QUARANTINE",
]


class AwsHealth:
    Type: str = "AWS Health Event"

    def create_finding(self, message: Dict[str, Any]) -> Finding:
        return Finding(
            compliance_item_type="aws_health",
            account=Account(identifier=message["detail"]["affectedAccount"]),
            item=message["detail"]["eventTypeCode"],
            region_name=message["region"],
            findings=self.build_finding(message),
            description=(
                "There is a new AWS Health event, "
                "you can view <https://health.aws.amazon.com/health/home#/account/dashboard/open-issues/|"
                "this in the console here>"
            ),
        )

    def create_pagerduty_event_payload(self, message: Dict[str, Any]) -> PagerDutyPayload:
        return PagerDutyPayload(
            compliance_item_type="aws_health",
            description=self.latest_description(message),
            source=message["detail"]["affectedAccount"],
            component=" ".join([e["entityValue"] for e in message["detail"]["affectedEntities"]]),
            event_class=message["detail"]["eventTypeCode"],
            group=message["detail"]["service"],
            timestamp=message["time"],
            account=Account(identifier=message["detail"]["affectedAccount"]),
            region_name=message["region"],
            custom_details=self.enrich_event_detail(message),
        )

    def enrich_event_detail(self, message: Dict[str, Any]) -> Dict[str, Any]:
        message_detail: Dict[str, Any] = message["detail"]
        for description in message_detail["eventDescription"]:
            if description["language"] == "en_US":
                description["runbook"] = RUNBOOK

        return message_detail

    def latest_description(self, message: Dict[str, Any]) -> str:
        latestDescription = "This event has no description"
        for description in message["detail"]["eventDescription"]:
            if description["language"] == "en_US":
                latestDescription = description["latestDescription"]

        return latestDescription

    def build_finding(self, message: Dict[str, Any]) -> Set[str]:
        return {self.latest_description(message)}

    def is_a_target_event_type(self, message: Dict[str, Any]) -> bool:
        return message["detail"]["eventTypeCode"] in EVENT_TYPE_CODES
