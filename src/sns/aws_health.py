from typing import Set, Dict, Any

from src.data.account import Account
from src.data.findings import Findings


class AwsHealth:
    Type: str = "AWS Health Event"

    def create_finding(self, message: Dict[str, Any]) -> Findings:
        return Findings(
            compliance_item_type="aws_health",
            account=Account(identifier=message["detail"]["affectedAccount"]),
            item=message["detail"]["eventTypeCode"],
            findings=self.build_description(message),
        )

    def build_description(self, message: Dict[str, Any]) -> Set[str]:
        latestDescription = "This event has no description"
        for description in message["detail"]["eventDescription"]:
            if description["language"] == "en_US":
                latestDescription = description["latestDescription"]

        link_text = (
            "There is a new AWS Heath event, "
            "you can view <https://health.aws.amazon.com/health/home#/account/dashboard/open-issues/|"
            "this in the console here>"
        )

        return {
            link_text,
            latestDescription,
        }
