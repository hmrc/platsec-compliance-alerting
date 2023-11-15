from unittest import TestCase
from unittest.mock import Mock

from src.clients.aws_ssm_client import AwsSsmClient
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.pagerduty_event import PagerDutyEvent
from src.data.pagerduty_payload import PagerDutyPayload
from src.pagerduty_notification_mapper import PagerDutyNotificationMapper

from tests.test_types_generator import _pagerduty_payload, account, finding

payload_a = _pagerduty_payload(source="1111", component="component-a", compliance_item_type="type-a")
payload_b = _pagerduty_payload(source="2222", component="component-b", compliance_item_type="type-b")
payload_c = _pagerduty_payload(source="3333", component="component-c", compliance_item_type="type-c")


def _pagerduty_event(payload: PagerDutyPayload, routing_key: str) -> PagerDutyEvent:
    return PagerDutyEvent(
        payload=payload,
        routing_key=routing_key,
        event_action='trigger',
        client='platsec-compliance-alerting',
        client_url='https://github.com/hmrc/platsec-compliance-alerting',
        links=[],
        images=[]
    )


class TestPagerDutyNotificationMapper(TestCase):
    def test_findings_mapper_with_compliance_item_type_mapping(self) -> None:
        mapping_0 = NotificationMappingConfig(channel="central", pagerduty_service="service-0")
        mapping_1 = NotificationMappingConfig(channel="channel-1", pagerduty_service="service-1", compliance_item_types=["type-b", "type-c"])
        mapping_2 = NotificationMappingConfig(channel="channel-2", pagerduty_service="service-2", compliance_item_types=["type-c", "type-a"])

        payloads = {payload_a, payload_b, payload_c}
        mappings = {mapping_0, mapping_1, mapping_2}

        mock_client = Mock(spec=AwsSsmClient)
        mock_client.get_parameter.side_effect = lambda parameter_name: f"{parameter_name.split('/')[-1]}-routing-key"

        pagerduty_events = PagerDutyNotificationMapper(mock_client).do_map(payloads, mappings)
        expected = [
            _pagerduty_event(payload=payload_a, routing_key="service-0-routing-key"),
            _pagerduty_event(payload=payload_a, routing_key="service-2-routing-key"),
            _pagerduty_event(payload=payload_b, routing_key="service-0-routing-key"),
            _pagerduty_event(payload=payload_b, routing_key="service-1-routing-key"),
            _pagerduty_event(payload=payload_c, routing_key="service-0-routing-key"),
            _pagerduty_event(payload=payload_c, routing_key="service-1-routing-key"),
            _pagerduty_event(payload=payload_c, routing_key="service-2-routing-key"),
        ]
        assert len(pagerduty_events) == 7
        assert expected == pagerduty_events

    def test_findings_mapper_with_account_mapping(self) -> None:
        mapping_0 = NotificationMappingConfig(channel="central", pagerduty_service="service-0")
        mapping_1 = NotificationMappingConfig(channel="channel-1", pagerduty_service="service-1", accounts=["2222"])
        mapping_2 = NotificationMappingConfig(channel="channel-2", pagerduty_service="service-2", accounts=["1111", "3333"])

        payloads = {payload_a, payload_b, payload_c}
        mappings = {mapping_0, mapping_1, mapping_2}

        mock_client = Mock(spec=AwsSsmClient)
        mock_client.get_parameter.side_effect = lambda parameter_name: f"{parameter_name.split('/')[-1]}-routing-key"

        pagerduty_events = PagerDutyNotificationMapper(mock_client).do_map(payloads, mappings)
        expected = [
            _pagerduty_event(payload=payload_a, routing_key="service-0-routing-key"),
            _pagerduty_event(payload=payload_a, routing_key="service-2-routing-key"),
            _pagerduty_event(payload=payload_b, routing_key="service-0-routing-key"),
            _pagerduty_event(payload=payload_b, routing_key="service-1-routing-key"),
            _pagerduty_event(payload=payload_c, routing_key="service-0-routing-key"),
            _pagerduty_event(payload=payload_c, routing_key="service-2-routing-key"),
        ]
        assert len(pagerduty_events) == 6
        assert expected == pagerduty_events

    def test_multiple_filter_configs(self) -> None:
        acct_a = account(name="a", identifier="1")
        mapping_1 = NotificationMappingConfig(channel="channel-1", pagerduty_service="service-1", accounts=["2222"], compliance_item_types=["type-b", "type-c"])
        mapping_2 = NotificationMappingConfig(channel="channel-2", pagerduty_service="service-2", accounts=["1111", "3333"], compliance_item_types=["type-b", "type-c"])

        payloads = {payload_a, payload_b, payload_c}
        mappings = {mapping_1, mapping_2}

        mock_client = Mock(spec=AwsSsmClient)
        mock_client.get_parameter.side_effect = lambda parameter_name: f"{parameter_name.split('/')[-1]}-routing-key"

        pagerduty_events = PagerDutyNotificationMapper(mock_client).do_map(payloads, mappings)
        expected = [
            _pagerduty_event(payload=payload_b, routing_key="service-1-routing-key"),
            _pagerduty_event(payload=payload_c, routing_key="service-2-routing-key"),
        ]
        assert len(pagerduty_events) == 2
        assert expected == pagerduty_events