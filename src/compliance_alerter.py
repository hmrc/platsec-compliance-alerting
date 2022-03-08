import logging
from logging import Logger
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


def main(event: Dict[str, Any]) -> None:
    logger = configure_logging()

    findings = handle_sns_event(event) if is_sns_event(event) else analyse(fetch(event))
    slack_messages = apply_mappings(apply_filters(findings))
    send(logger, slack_messages)


def configure_logging() -> Logger:
    logger = logging.getLogger()
    logger.setLevel(Config.get_log_level())
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("s3transfer").setLevel(logging.ERROR)
    return logger


def is_sns_event(event: Dict[str, Any]) -> bool:
    return "EventSource" in event.get("Records", [{}])[0] and event["Records"][0].get("EventSource") == "aws:sns"


def handle_sns_event(events: Dict[str, Any]) -> Set[Findings]:
    findings: Set[Findings] = set()
    for record in events["Records"]:
        message = json.loads(record["Sns"]["Message"])
        type = message.get("detailType") or message.get("detail-type")
        if type == CodePipeline.Type:
            findings.add(CodePipeline().create_finding(message))
        elif type == CodeBuild.Type:
            findings.add(CodeBuild().create_finding(message))
        elif type == GuardDuty.Type:
            findings.add(GuardDuty(config).create_finding(message))
        else:
            logging.getLogger(__name__).warning(f"Received unknown event with detailType '{type}'. Ignoring...")
    return findings


def fetch(event: Dict[str, Any]) -> Audit:
    return AuditFetcher().fetch_audit(config.get_report_s3_client(), event)


def analyse(audit: Audit) -> Set[Findings]:
    return AuditAnalyser().analyse(audit, config)


def apply_filters(notifications: Set[Findings]) -> Set[Findings]:
    return FindingsFilter().do_filter(notifications, config.get_notification_filters())


def apply_mappings(notifications: Set[Findings]) -> List[SlackMessage]:
    return NotificationMapper().do_map(notifications, config.get_notification_mappings(), config.get_org_client())


def send(logger: Logger, slack_messages: List[SlackMessage]) -> None:
    logger.debug("Sending the following messages: %s", slack_messages)
    SlackNotifier(config.get_slack_notifier_config()).send_messages(slack_messages)
