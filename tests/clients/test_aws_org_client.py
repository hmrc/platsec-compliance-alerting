from moto import mock_organizations

from src.clients.aws_org_client import AwsOrgClient

import boto3


@mock_organizations  # type: ignore
def test_get_account_details() -> None:
    client = boto3.client("organizations")

    client.create_organization(FeatureSet="ALL")
    account_id = client.create_account(AccountName="test-account-name", Email="example@example.com")[
        "CreateAccountStatus"
    ]["AccountId"]
    client.tag_resource(
        ResourceId=account_id,
        Tags=[
            {"Key": "team_slack_handle", "Value": "@platsec"},
        ],
    )

    result = AwsOrgClient(client).get_account(account_id=account_id)

    assert result.name == "test-account-name"
    assert result.identifier == account_id
    assert result.slack_handle == "@platsec"


@mock_organizations  # type: ignore
def test_get_slack_handle() -> None:
    client = boto3.client("organizations")

    client.create_organization(FeatureSet="ALL")
    account_id = client.create_account(AccountName="test-account-name", Email="example@example.com")[
        "CreateAccountStatus"
    ]["AccountId"]

    client.tag_resource(
        ResourceId=account_id,
        Tags=[
            {"Key": "team_slack_handle", "Value": "@platsec"},
        ],
    )

    result = AwsOrgClient(client)._get_slack_handle(account_id=account_id)

    assert result == "@platsec"


@mock_organizations  # type: ignore
def test_get_account_details_when_missing_tags() -> None:
    client = boto3.client("organizations")

    client.create_organization(FeatureSet="ALL")
    account_id = client.create_account(AccountName="test-account-name", Email="example@example.com")[
        "CreateAccountStatus"
    ]["AccountId"]

    result = AwsOrgClient(client).get_account(account_id=account_id)

    assert result.name == "test-account-name"
    assert result.identifier == account_id
    assert result.slack_handle == "owning-team-not-found"


@mock_organizations  # type: ignore
def test_get_account_details_fails() -> None:
    client = boto3.client("organizations")

    result = AwsOrgClient(client).get_account(account_id="49857")

    assert result.name == "account not found"
    assert result.slack_handle == "owning-team-not-found"
    assert result.identifier == "49857"
