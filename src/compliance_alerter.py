from typing import Any, Dict, List, Set

from src.audit_analyser import AuditAnalyser
from src.audit_fetcher import AuditFetcher
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.findings_filter import FindingsFilter
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage, SlackNotifier
from src.sns.codepipeline import CodePipeline

config = Config()


def main(event: Dict[str, Any]) -> None:
    if "EventSource" in event["Records"][0] and event["Records"][0]["EventSource"] == "aws:sns":
        findings = CodePipeline().event_to_findings(event)
    else:
        findings = analyse(fetch(event))

    slack_messages = map(filter(findings))
    send(slack_messages)


def fetch(event: Dict[str, Any]) -> Audit:
    return AuditFetcher().fetch_audit(config.get_report_s3_client(), event)


def analyse(audit: Audit) -> Set[Findings]:
    return AuditAnalyser().analyse(audit, config)


def filter(notifications: Set[Findings]) -> Set[Findings]:
    return FindingsFilter().do_filter(notifications, config.get_notification_filters())


def map(notifications: Set[Findings]) -> List[SlackMessage]:
    return NotificationMapper().do_map(notifications, config.get_notification_mappings())


def send(slack_messages: List[SlackMessage]) -> None:
    SlackNotifier(config.get_slack_notifier_config()).send_messages(slack_messages)
