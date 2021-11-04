from typing import Any, Dict, List, Set

from src.audit_analyser import AuditAnalyser
from src.audit_fetcher import AuditFetcher
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.findings_filter import FindingsFilter
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage, SlackNotifier

config = Config()


def main(event: Dict[str, Any]) -> None:
    send(map(filter(analyse(fetch(event)))))


def fetch(event: Dict[str, Any]) -> Audit:
    return AuditFetcher().fetch_audit(config.get_report_s3_client(), event)


def analyse(audit: Audit) -> Set[Findings]:
    return AuditAnalyser().analyse(audit, config)


def filter(notifications: Set[Findings]) -> Set[Findings]:
    return FindingsFilter().do_filter(notifications, config.get_notification_filters())


def map(notifications: Set[Findings]) -> List[SlackMessage]:
    return NotificationMapper().do_map(notifications, config.get_notification_mappings(), config.get_central_channel())


def send(slack_messages: List[SlackMessage]) -> None:
    SlackNotifier(config.get_slack_notifier_config()).send_messages(slack_messages)
