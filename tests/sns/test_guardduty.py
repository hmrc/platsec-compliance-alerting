import json

from unittest.mock import Mock, patch

from src.config.config import Config
from src.sns.guardduty import GuardDuty

from tests.sns import load_json_resource


@patch.object(Config, "get_account_mappings", return_value={"123456789012": "account-1"})
@patch.object(Config, "get_guardduty_runbook_url", return_value="the-runbook-url")
@patch.object(Config, "get_slack_mappings", return_value={"team-a": ["account-1", "account-2"]})
def test_event_to_findings(*_: Mock) -> None:
    message = json.loads(load_json_resource("guardduty_event.json")["Records"][0]["Sns"]["Message"])

    finding = GuardDuty(Config()).create_finding(message)

    assert finding.account.identifier == "123456789012"
    assert finding.account.name == "account-1"
    assert finding.description == "Amazon S3 Block Public Access was disabled for S3 bucket test-gd-32423."
    assert finding.compliance_item_type == "guardduty"
    assert finding.item == "GuardDuty alert"
    assert finding.findings == {
        "*Type:* `Policy:S3/BucketBlockPublicAccessDisabled`",
        "*Severity:* `2`",
        "*Team:* <team-a>",
        "*First seen:* 2022-03-01T14:20:48.000Z",
        "*Last seen:* 2022-03-01T14:20:49.000Z",
        (
            "*Links:* <https://eu-west-2.console.aws.amazon.com/guardduty/home?region=eu-west-2#/findings?fId=a6bfa2f07"
            "|GuardDuty Console> <the-runbook-url|Runbook>"
        ),
    }
