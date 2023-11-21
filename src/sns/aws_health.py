from typing import Set, Dict, Any

from src.data.account import Account
from src.data.finding import Finding
from src.data.pagerduty_payload import PagerDutyPayload


class AwsHealth:
    Type: str = "AWS Health Event"

    def create_finding(self, message: Dict[str, Any]) -> Finding:
        return Finding(
            compliance_item_type="aws_health",
            account=Account(identifier=message["detail"]["affectedAccount"]),
            item=message["detail"]["eventTypeCode"],
            region_name=message["region"],
            findings=self.build_description(message),
            description=(
                "There is a new AWS Health event, "
                "you can view <https://health.aws.amazon.com/health/home#/account/dashboard/open-issues/|"
                "this in the console here>"
            ),
        )

    def create_pagerduty_event_payload(self, message: Dict[str, Any]) -> PagerDutyPayload:
        latestDescription = "This event has no description"
        for description in message["detail"]["eventDescription"]:
            if description["language"] == "en_US":
                latestDescription = description["latestDescription"]

        return PagerDutyPayload(
            compliance_item_type="aws_health",
            description=latestDescription,
            source=message["detail"]["affectedAccount"],
            component=" ".join(message["resources"]),
            event_class=message["detail"]["eventTypeCode"],
            group=message["detail"]["service"],
            timestamp=message["time"],
            account=Account(identifier=message["detail"]["affectedAccount"]),
            region_name=message["region"],
            custom_details=message["detail"],
        )

    def build_description(self, message: Dict[str, Any]) -> Set[str]:
        latestDescription = "This event has no description"
        for description in message["detail"]["eventDescription"]:
            if description["language"] == "en_US":
                latestDescription = description["latestDescription"]

        return {latestDescription}
