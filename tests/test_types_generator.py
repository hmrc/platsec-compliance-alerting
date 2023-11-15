import random
import string
from typing import Optional, Set, List, Dict, Any

from src.data.account import Account
from src.data.audit import Audit
from src.data.finding import Finding
from src.data.pagerduty_event import PagerDutyEvent
from src.data.pagerduty_payload import PagerDutyPayload
from src.data.severity import Severity


def account(identifier: str = "1234", name: str = "test-account") -> Account:
    return Account(identifier=identifier, name=name)


def create_account() -> Account:
    return Account(
        identifier=str(random.randrange(100000000000, 1000000000000)),
        name=f"account-{''.join(random.choices(string.ascii_letters, k=15))}",
    )


def finding(
    severity: Severity = Severity.HIGH,
    account: Optional[Account] = account(),
    compliance_item_type: str = "item_type",
    item: str = "test-item",
    region_name: Optional[str] = "test-region-name",
    findings: Optional[Set[str]] = None,
    description: Optional[str] = None,
) -> Finding:
    return Finding(
        severity=severity,
        account=account,
        region_name=region_name,
        compliance_item_type=compliance_item_type,
        item=item,
        description=description,
        findings=findings,
    )


def create_audit(report: List[Dict[str, Any]], type: str = "iam_access_keys") -> Audit:
    return Audit(type=type, report=report)


def _pagerduty_payload(source: str, component: str, compliance_item_type: str = "aws_health"):
    return PagerDutyPayload(
        compliance_item_type=compliance_item_type,
        description="A description of the event",
        source=source,
        component=component,
        event_class="eventTypeCode",
        group="EC2",
        timestamp="2022-06-03T06:27:57Z",
        account=Account(identifier=source),
        region_name="a-region",
        custom_details={},
    )


def _pagerduty_event(payload: PagerDutyPayload, service: str) -> PagerDutyEvent:
    return PagerDutyEvent(
        payload=payload,
        routing_key=f"{service}-routing-key",
        event_action="trigger",
        client="platsec-compliance-alerting",
        client_url="https://github.com/hmrc/platsec-compliance-alerting",
        links=[],
        images=[],
        service=service,
    )
