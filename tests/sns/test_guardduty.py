import json

from unittest.mock import Mock, patch

from src.config.config import Config
from src.sns.guardduty import GuardDuty

from tests.sns import load_json_resource


@patch.object(Config, "get_guardduty_runbook_url", return_value="the-runbook-url")
def test_event_to_findings(*_: Mock) -> None:
    message = json.loads(load_json_resource("guardduty_event.json")["Records"][0]["Sns"]["Message"])

    finding = GuardDuty(Config()).create_finding(message)

    assert finding.account
    assert finding.account.identifier == "987654321098"
    assert finding.account.name == ""
    assert finding.description == "Amazon S3 Block Public Access was disabled for S3 bucket test-gd-32423."
    assert finding.compliance_item_type == "guardduty"
    assert finding.item == "GuardDuty alert"
    assert finding.findings == {
        "*Type:* `Policy:S3/BucketBlockPublicAccessDisabled`",
        "*Severity:* `2`",
        "*Timestamp:* 2022-03-01 14:20:49+00:00",
        (
            "*Links:* <https://eu-west-2.console.aws.amazon.com/guardduty/home?region=eu-west-2#/findings?fId=a6bfa2f07"
            "|GuardDuty Console> | <the-runbook-url|Runbook>"
        ),
        "*Region:* eu-west-2",
    }
