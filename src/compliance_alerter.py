import logging
from logging import Logger
from typing import Any, Dict, List, Set
import json

from src.audit_analyser import AuditAnalyser
from src.audit_fetcher import AuditFetcher
from src.clients.aws_client_factory import AwsClientFactory
from src.clients.aws_ssm_client import AwsSsmClient
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.findings_filter import FindingsFilter
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage, SlackNotifier
from src.sns.codebuild import CodeBuild
from src.sns.codepipeline import CodePipeline
from src.sns.guardduty import GuardDuty


def main(event: Dict[str, Any]) -> None:
    compliance_alerter = ComplianceAlerter(
        config=Config(
            config_s3_client=AwsClientFactory().get_s3_client(
                Config.get_aws_account(), Config.get_config_bucket_read_role()
            ),
            report_s3_client=AwsClientFactory().get_s3_client(
                Config.get_aws_account(), Config.get_report_bucket_read_role()
            ),
            ssm_client=AwsClientFactory().get_ssm_client(Config.get_aws_account(), Config.get_ssm_read_role()),
            org_client=AwsClientFactory().get_org_client(Config.get_org_account(), Config.get_org_read_role()),
        )
    )
    compliance_alerter.send(compliance_alerter.generate_slack_messages(event))


class ComplianceAlerter:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = Config.configure_logging()

    def generate_slack_messages(self, event: Dict[str, Any]) -> List[SlackMessage]:
        findings = (
            self.handle_sns_event(event) if ComplianceAlerter.is_sns_event(event) else self.analyse(self.fetch(event))
        )
        slack_messages = self.apply_mappings(self.apply_filters(findings))
        return slack_messages

    @staticmethod
    def is_sns_event(event: Dict[str, Any]) -> bool:
        return "EventSource" in event.get("Records", [{}])[0] and event["Records"][0].get("EventSource") == "aws:sns"

    def handle_sns_event(self, events: Dict[str, Any]) -> Set[Findings]:
        findings: Set[Findings] = set()
        for record in events["Records"]:
            message = json.loads(record["Sns"]["Message"])
            type = message.get("detailType") or message.get("detail-type")
            if type == CodePipeline.Type:
                findings.add(CodePipeline().create_finding(message))
            elif type == CodeBuild.Type:
                findings.add(CodeBuild().create_finding(message))
            elif type == GuardDuty.Type:
                findings.add(GuardDuty(self.config).create_finding(message))
            else:
                logging.getLogger(__name__).warning(f"Received unknown event with detailType '{type}'. Ignoring...")
        return findings

    def fetch(self, event: Dict[str, Any]) -> Audit:
        return AuditFetcher().fetch_audit(self.config.get_report_s3_client(), event)

    def analyse(self, audit: Audit) -> Set[Findings]:
        return AuditAnalyser().analyse(self.logger, audit, self.config)

    def apply_filters(self, notifications: Set[Findings]) -> Set[Findings]:
        return FindingsFilter().do_filter(notifications, self.config.get_notification_filters())

    def apply_mappings(self, notifications: Set[Findings]) -> List[SlackMessage]:
        return NotificationMapper().do_map(
            notifications, self.config.get_notification_mappings(), self.config.org_client
        )

    def send(self, slack_messages: List[SlackMessage]) -> None:
        self.logger.debug("Sending the following messages: %s", slack_messages)
        print(self.config.get_slack_notifier_config())
        print(slack_messages)
        SlackNotifier(self.config.get_slack_notifier_config()).send_messages(slack_messages)
