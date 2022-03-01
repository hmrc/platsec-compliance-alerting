import json

from src.sns.guardduty import GuardDuty

from tests.sns import load_json_resource


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("guardduty_event.json")["Records"][0]["Sns"]["Message"])

    finding = GuardDuty().create_finding(message)
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "guardduty"
    assert finding.item == "{'AWS::S3::Bucket': 'test-gd-324237984731208478901374'}"
    assert finding.findings == {"Policy:S3/BucketBlockPublicAccessDisabled"}
