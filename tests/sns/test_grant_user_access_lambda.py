import json

from src.sns.grant_user_access_lambda import GrantUserAccessLambda

from tests.sns import load_json_resource


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("grant_user_access_lambda_event.json")["Records"][0]["Sns"]["Message"])

    finding = GrantUserAccessLambda().create_finding(message)
    assert finding.account
    assert finding.account.identifier == "0987654321"
    assert finding.compliance_item_type == "grant_user_access_lambda"
    assert finding.item == "Temporary access to user(s) granted"
    assert len(finding.findings) == 1

    expected_notification_text = (
        "Access to `arn:aws:iam::0987654321:role/RoleTestSSMAccess` has been granted "
        "for 1 hour(s) to the following users at 2023-09-14T13:09:38Z:\n  *  test-user01\n  *  test-user02\n"
        "Access expires at 2023-09-14T14:09:38Z."
    )
    assert finding.findings == frozenset({expected_notification_text})
