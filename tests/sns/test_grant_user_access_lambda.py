import json

from src.sns.codebuild import CodeBuild
from src.sns.grant_user_access_lambda import GrantUserAccessLambda

from tests.sns import load_json_resource


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("grant_user_access_lambda_event.json")["Records"][0]["Sns"]["Message"])

    finding = GrantUserAccessLambda().create_finding(message)
    assert finding.account
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "grant_user_access_lambda"
    assert finding.item == "arn:aws:iam::123456789012:role/RoleTestSSMAccess access granted"
    assert len(finding.findings) == 1

    expected_notification_text = (
            "Access to arn:aws:iam::123456789012:role/RoleTestSSMAccess has been granted by approval.user "
            "for 1 hour(s) to the following users at 2023-09-14T13:09:38Z:\ntest-user01\ntest-user02\n"
            "Access expires at 2023-09-14T14:09:38Z."
        )
    assert finding.findings == frozenset({expected_notification_text})
