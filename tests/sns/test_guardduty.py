import json

from unittest.mock import patch

from src.config.config import Config
from src.sns.guardduty import GuardDuty

from tests.sns import load_json_resource


@patch.object(Config, "get_guardduty_runbook_url", "the-runbook")
def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("guardduty_event.json")["Records"][0]["Sns"]["Message"])

    finding = GuardDuty(Config()).create_finding(message)

    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "guardduty"
    assert finding.item == "{'AWS::S3::Bucket': 'test-gd-324237984731208478901374'}"
    assert finding.findings == {
        "Type: Policy:S3/BucketBlockPublicAccessDisabled",
        "Severity: 2",
        "Account: 123456789012",
        (
            "Details: https://eu-west-2.console.aws.amazon.com/guardduty/home?region=eu-west-2#/findings?macros=current"
            "&fId=a6bfa2f07893be4f3c3174d5af7e2f80"
        ),
        "First seen: 2022-03-01T14:20:48.000Z",
        "Last seen: 2022-03-01T14:20:49.000Z",
        "Runbook: the-runbook",
    }
