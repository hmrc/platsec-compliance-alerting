from src.sns.aws_health import RUNBOOK, AwsHealth

from tests.sns import load_json_resource


def test_event_to_findings() -> None:
    message = load_json_resource("health_message_aws_risk_credentials_exposed.json")

    finding = AwsHealth().create_finding(message)

    assert finding.account
    assert finding.region_name == "us-east-1"
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "aws_health"
    assert finding.item == "AWS_RISK_CREDENTIALS_EXPOSED"
    assert len(finding.findings) == 1

    assert finding.description == (
        "There is a new AWS Health event,"
        " you can view <https://health.aws.amazon.com/health/home#/account/dashboard/open-issues/|"
        "this in the console here>"
    )

    assert finding.findings == frozenset({"A description of the event is provided here"})


def test_create_pagerduty_event_payload() -> None:
    payload = AwsHealth().create_pagerduty_event_payload(
        load_json_resource("health_message_aws_risk_credentials_exposed.json")
    )

    assert payload.account
    assert payload.account.identifier == "123456789012"
    assert payload.source == "123456789012"
    assert payload.group == "RISK"

    expected = load_json_resource("health_message_aws_risk_credentials_exposed.json")
    expected["detail"]["eventDescription"] = [
        {
            "language": "en_US",
            "latestDescription": "A description of the event is provided here",
            "runbook": RUNBOOK,
        }
    ]
    assert payload.custom_details == expected["detail"]


def test_is_a_target_event_type() -> None:
    assert (
        AwsHealth().is_a_target_event_type(load_json_resource("health_message_aws_risk_credentials_exposed.json"))
        is True
    )
    assert (
        AwsHealth().is_a_target_event_type(
            load_json_resource("health_message_aws_ec2_instance_store_drive_performance_degraded.json")
        )
        is False
    )
