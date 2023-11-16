from src.sns.aws_health import AwsHealth

from tests.sns import load_json_resource


def test_event_to_findings() -> None:
    message = load_json_resource("health_message.json")

    finding = AwsHealth().create_finding(message)

    assert finding.account
    assert finding.region_name == "us-west-2"
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "aws_health"
    assert finding.item == "AWS_EC2_INSTANCE_STORE_DRIVE_PERFORMANCE_DEGRADED"
    assert len(finding.findings) == 1

    assert finding.description == (
        "There is a new AWS Health event,"
        " you can view <https://health.aws.amazon.com/health/home#/account/dashboard/open-issues/|"
        "this in the console here>"
    )

    assert finding.findings == frozenset({"A description of the event will be provided here"})
