from logging import getLogger
from typing import Any, Dict, List, Set
import json

from src.audit_analyser import AuditAnalyser
from src.audit_fetcher import AuditFetcher
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.findings_filter import FindingsFilter
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage, SlackNotifier
from src.sns.codebuild import CodeBuild
from src.sns.codepipeline import CodePipeline
from src.sns.guardduty import GuardDuty

config = Config()


def main(events: Dict[str, Any]) -> None:
    if "EventSource" in events["Records"][0] and events["Records"][0]["EventSource"] == "aws:sns":
        findings = handle_sns_events(events)
    else:
        findings = analyse(fetch(events))

    slack_messages = map(filter(findings))
    send(slack_messages)


def handle_sns_events(events: Dict[str, Any]) -> Set[Findings]:
    findings: Set[Findings] = set()
    for record in events["Records"]:
        message = json.loads(record["Sns"]["Message"])
        type = message.get("detailType") or message.get("detail-type")
        if type == CodePipeline.Type:
            findings.add(CodePipeline().create_finding(message))
        elif type == CodeBuild.Type:
            findings.add(CodeBuild().create_finding(message))
        elif type == GuardDuty.Type:
            findings.add(GuardDuty().create_finding(message))
        else:
            getLogger(__name__).warning(f"Received unknown event with detailType '{type}'. Ignoring...")
    return findings


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
