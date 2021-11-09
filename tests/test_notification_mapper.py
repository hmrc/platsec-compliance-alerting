from unittest import TestCase

from src.config.notification_mapping_config import NotificationMappingConfig
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage

from tests.test_types_generator import account, findings


findings_a = findings(item="item-a", findings={"a-1", "a-2"}, account=account(identifier="111", name="bbb"))
findings_b = findings(item="item-b", findings={"finding b"}, account=account(identifier="222", name="aaa"))
findings_c = findings(item="item-c", findings={"finding c"}, account=account(identifier="333", name="ccc"))

msg_a = SlackMessage(["central", "channel-2"], "bbb (111)", "item-a", "a-1\na-2", "#ff4d4d")
msg_b = SlackMessage(["central", "channel-1"], "aaa (222)", "item-b", "finding b", "#ff4d4d")
msg_c = SlackMessage(["central", "channel-1", "channel-2"], "ccc (333)", "item-c", "finding c", "#ff4d4d")


class TestNotificationMapper(TestCase):
    def test_findings_mapper_with_items_mapping(self) -> None:
        mapping_0 = NotificationMappingConfig("central")
        mapping_1 = NotificationMappingConfig("channel-1", items=["item-b", "item-c"])
        mapping_2 = NotificationMappingConfig("channel-2", items=["item-c", "item-a"])

        all_findings = {findings_a, findings_b, findings_c}
        mappings = {mapping_0, mapping_1, mapping_2}
        slack_messages = NotificationMapper().do_map(all_findings, mappings)
        self.assertEqual([msg_b, msg_a, msg_c], slack_messages)

    def test_findings_mapper_with_account_mapping(self) -> None:
        mapping_0 = NotificationMappingConfig("central")
        mapping_1 = NotificationMappingConfig("channel-1", accounts=["222"])
        mapping_2 = NotificationMappingConfig("channel-1", accounts=["333"])
        mapping_3 = NotificationMappingConfig("channel-2", accounts=["111", "333"])

        all_findings = {findings_a, findings_b, findings_c}
        mappings = {mapping_0, mapping_1, mapping_2, mapping_3}
        slack_messages = NotificationMapper().do_map(all_findings, mappings)
        self.assertEqual([msg_b, msg_a, msg_c], slack_messages)

    def test_can_send_item_types_to_specific_channel(self) -> None:
        mapping_1 = NotificationMappingConfig("channel-1", compliance_item_types=["s3_bucket"])
        mapping_2 = NotificationMappingConfig("channel-2", compliance_item_types=["iam_access_key"])

        bucket_findings = findings(compliance_item_type="s3_bucket", account=account(name="a"))
        access_key_findings = findings(compliance_item_type="iam_access_key", account=account(name="b"))
        slack_messages = NotificationMapper().do_map(
            {bucket_findings, access_key_findings},
            {mapping_1, mapping_2},
        )
        self.assertIn("channel-1", slack_messages[0].channels)
        self.assertIn("channel-2", slack_messages[1].channels)

    def test_channel_with_no_filters_gets_all_notifications(self) -> None:
        mapping = NotificationMappingConfig("all-channel")
        bucket_findings = findings(compliance_item_type="s3_bucket", account=account(name="a"))
        access_key_findings = findings(compliance_item_type="iam_access_key", account=account(name="b"))

        slack_messages = NotificationMapper().do_map(
            {bucket_findings, access_key_findings},
            {mapping},
        )

        self.assertEqual(2, len(slack_messages))
        self.assertEqual([["all-channel"], ["all-channel"]], [sm.channels for sm in slack_messages])

    def test_multiple_filter_configs(self) -> None:
        acct_a = account(name="a", identifier="1")
        mapping_1 = NotificationMappingConfig("channel-1", accounts=[acct_a.identifier])
        mapping_2 = NotificationMappingConfig(
            "channel-2", accounts=[acct_a.identifier], compliance_item_types=["s3_bucket"]
        )
        bucket_findings = findings(compliance_item_type="s3_bucket", account=acct_a, item="bucket")
        access_key_findings = findings(compliance_item_type="iam_access_key", account=acct_a, item="key")
        unmapped_findings = findings(compliance_item_type="s3_bucket", account=account(name="b", identifier="2"))

        slack_messages = NotificationMapper().do_map(
            {bucket_findings, access_key_findings, unmapped_findings},
            {mapping_1, mapping_2},
        )

        ch_1_messages = [sm for sm in slack_messages if "channel-1" in sm.channels]
        self.assertEqual(2, len(ch_1_messages))
        ch_2_messages = [sm for sm in slack_messages if "channel-2" in sm.channels]
        self.assertEqual(1, len(ch_2_messages))
        self.assertEqual("bucket", ch_2_messages[0].title)

    def test_findings_mapper_with_description(self) -> None:
        description = "additional context about the item"
        f = findings(description=description, findings={"finding-a", "finding-b"})

        slack_messages = NotificationMapper().do_map({f}, set())

        expected_text = f"{description}\n\nfinding-a\nfinding-b"
        self.assertEqual(expected_text, slack_messages[0].text)
