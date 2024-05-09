from unittest import TestCase
from unittest.mock import Mock
from typing import Any
import pytest

from src.clients.aws_org_client import AwsOrgClient
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.account import Account
from src.data.severity import Severity
from src.data.slack_message import SlackMessage
from src.notification_mapper import NotificationMapper

from tests.test_types_generator import account, finding


SLACK_EMOJI = ":test-emoji:"
SERVICE_NAME = "test-service"
findings_a = finding(
    severity=Severity.HIGH, item="item-a", findings={"a-1", "a-2"}, account=account(identifier="111", name="bbb")
)
findings_b = finding(item="item-b", findings={"finding b"}, account=account(identifier="222", name="aaa"))
findings_c = finding(
    severity=Severity.LOW, item="item-c", findings={"finding c"}, account=account(identifier="333", name="ccc")
)


@pytest.fixture(autouse=True)
def _setup_environment(monkeypatch: Any) -> None:
    env_vars = {
        "SLACK_EMOJI": SLACK_EMOJI,
        "SERVICE_NAME": SERVICE_NAME,
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)


msg_a = SlackMessage(
    channels=["central", "channel-2"],
    heading="aaa (111) test-region-name team-a",
    title="item-a",
    text="a-1\na-2",
    color="#ff4d4d",
    emoji=":test-emoji:",
    source="test-service",
)
msg_b = SlackMessage(
    channels=["central", "channel-1"],
    heading="bbb (222) test-region-name team-a",
    title="item-b",
    text="finding b",
    color="#ff4d4d",
    emoji=":test-emoji:",
    source="test-service",
)
msg_c = SlackMessage(
    channels=["central", "channel-1", "channel-2"],
    heading="ccc (333) test-region-name team-b",
    title="item-c",
    text="finding c",
    color="#ffffff",
    emoji=":test-emoji:",
    source="test-service",
)


class TestNotificationMapper(TestCase):
    def test_findings_mapper_with_items_mapping(self) -> None:
        mapping_0 = NotificationMappingConfig("central")
        mapping_1 = NotificationMappingConfig("channel-1", items=["item-b", "item-c"])
        mapping_2 = NotificationMappingConfig("channel-2", items=["item-c", "item-a"])

        all_findings = {findings_a, findings_b, findings_c}
        mappings = {mapping_0, mapping_1, mapping_2}

        mock_client = Mock(spec=AwsOrgClient)
        mock_client.get_account.side_effect = lambda account_id: Account(
            name=({"111": "aaa", "222": "bbb", "333": "ccc"}[account_id]),
            identifier=account_id,
            slack_handle=({"111": "team-a", "222": "team-a", "333": "team-b"}[account_id]),
        )

        slack_messages = NotificationMapper().do_map(all_findings, mappings, mock_client)
        assert slack_messages == [msg_a, msg_b, msg_c]

    def test_findings_mapper_with_account_mapping(self) -> None:
        mapping_0 = NotificationMappingConfig("central")
        mapping_1 = NotificationMappingConfig("channel-1", accounts=["222"])
        mapping_2 = NotificationMappingConfig("channel-1", accounts=["333"])
        mapping_3 = NotificationMappingConfig("channel-2", accounts=["111", "333"])

        all_findings = {findings_a, findings_b, findings_c}
        mappings = {mapping_0, mapping_1, mapping_2, mapping_3}

        mock_client = Mock(spec=AwsOrgClient)
        mock_client.get_account.side_effect = lambda account_id: Account(
            name=({"111": "aaa", "222": "bbb", "333": "ccc"}[account_id]),
            identifier=account_id,
            slack_handle={"111": "team-a", "222": "team-a", "333": "team-b"}[account_id],
        )

        slack_messages = NotificationMapper().do_map(all_findings, mappings, mock_client)
        assert slack_messages == [msg_a, msg_b, msg_c]

    def test_can_send_item_types_to_specific_channel(self) -> None:
        mapping_1 = NotificationMappingConfig("channel-1", compliance_item_types=["s3_bucket"])
        mapping_2 = NotificationMappingConfig("channel-2", compliance_item_types=["iam_access_key"])

        bucket_findings = finding(
            item="test-1", compliance_item_type="s3_bucket", account=account(name="aaa", identifier="111")
        )
        access_key_findings = finding(
            item="test-2", compliance_item_type="iam_access_key", account=account(name="bbb", identifier="222")
        )

        mock = Mock(spec=AwsOrgClient)
        mock.get_account.return_value = account()

        slack_messages = NotificationMapper().do_map(
            {bucket_findings, access_key_findings}, {mapping_1, mapping_2}, mock
        )
        assert "channel-1" in slack_messages[0].channels
        assert "channel-2" in slack_messages[1].channels

    def test_channel_with_no_filters_gets_all_notifications(self) -> None:
        mapping = NotificationMappingConfig("all-channel")
        bucket_findings = finding(compliance_item_type="s3_bucket", account=account(name="a"))
        access_key_findings = finding(compliance_item_type="iam_access_key", account=account(name="b"))

        mock_client = Mock(spec=AwsOrgClient)
        mock_client.get_account.side_effect = lambda account_id: Account(
            name=({"1234": "team-a"}[account_id]), identifier=account_id
        )

        slack_messages = NotificationMapper().do_map({bucket_findings, access_key_findings}, {mapping}, mock_client)

        self.assertEqual(2, len(slack_messages))
        self.assertEqual([["all-channel"], ["all-channel"]], [sm.channels for sm in slack_messages])

    def test_multiple_filter_configs(self) -> None:
        acct_a = account(name="a", identifier="1")
        mapping_1 = NotificationMappingConfig("channel-1", accounts=[acct_a.identifier])
        mapping_2 = NotificationMappingConfig(
            "channel-2", accounts=[acct_a.identifier], compliance_item_types=["s3_bucket"]
        )
        bucket_findings = finding(compliance_item_type="s3_bucket", account=acct_a, item="bucket")
        access_key_findings = finding(compliance_item_type="iam_access_key", account=acct_a, item="key")
        unmapped_findings = finding(compliance_item_type="s3_bucket", account=account(name="b", identifier="2"))

        mock_client = Mock(spec=AwsOrgClient)
        mock_client.get_account.side_effect = lambda account_id: Account(
            name={"1": "aaa", "2": "bbb"}[account_id],
            identifier=account_id,
            slack_handle={"1": "team-a", "2": "team-b"}[account_id],
        )

        slack_messages = NotificationMapper().do_map(
            {bucket_findings, access_key_findings, unmapped_findings}, {mapping_1, mapping_2}, mock_client
        )

        ch_1_messages = [sm for sm in slack_messages if "channel-1" in sm.channels]
        self.assertEqual(2, len(ch_1_messages))
        ch_2_messages = [sm for sm in slack_messages if "channel-2" in sm.channels]
        self.assertEqual(1, len(ch_2_messages))
        self.assertEqual("bucket", ch_2_messages[0].title)

    def test_findings_mapper_with_description(self) -> None:
        description = "additional context about the item"
        f = finding(description=description, findings={"finding-a", "finding-b"})

        slack_messages = NotificationMapper().do_map({f}, set(), Mock(spec=AwsOrgClient))

        expected_text = f"{description}\n\nfinding-a\nfinding-b"
        self.assertEqual(expected_text, slack_messages[0].text)
