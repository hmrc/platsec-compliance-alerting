import logging
from typing import Any, Dict, Set, TypeVar
import json

from src.audit_analyser import AuditAnalyser
from src.audit_fetcher import AuditFetcher
from src.clients.aws_client_factory import AwsClientFactory
from src.config.config import Config
from src.data.audit import Audit
from src.data.finding import Finding
from src.data.pagerduty_payload import PagerDutyPayload
from src.notifiers.notifier import Notifier
from src.notifiers.pagerduty_notifier import PagerDutyNotifier
from src.notifiers.slack_notifier import SlackNotifier
from src.sns.codebuild import CodeBuild
from src.sns.codepipeline import CodePipeline
from src.sns.grant_user_access_lambda import GrantUserAccessLambda
from src.sns.guardduty import GuardDuty
from src.sns.aws_health import AwsHealth

N = TypeVar("N")
P = TypeVar("P")


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

    if compliance_alerter.is_sns_event(event=event):
        compliance_alerter.send(
            notifier=SlackNotifier(config=compliance_alerter.config),
            payloads=compliance_alerter.build_sns_event_findings(event=event),
        )
        compliance_alerter.send(
            notifier=PagerDutyNotifier(config=compliance_alerter.config),
            payloads=compliance_alerter.build_pagerduty_payloads(event=event),
        )

    if compliance_alerter.is_s3_event(event=event):
        compliance_alerter.logger.info("S3 event received")
        compliance_alerter.send(
            notifier=SlackNotifier(config=compliance_alerter.config),
            payloads=compliance_alerter.build_audit_report_findings(event=event),
        )


class ComplianceAlerter:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = Config.configure_logging()
        self.logger.info("ComplianceAlerter initialised")

    @staticmethod
    def event_source(event: Dict[str, Any]) -> str:
        source = ""
        if "EventSource" in event.get("Records", [{}])[0]:
            source = event["Records"][0].get("EventSource")

        if "eventSource" in event.get("Records", [{}])[0]:
            source = event["Records"][0].get("eventSource")

        return source

    @staticmethod
    def is_sns_event(event: Dict[str, Any]) -> bool:
        return ComplianceAlerter.event_source(event=event) == "aws:sns"

    @staticmethod
    def is_s3_event(event: Dict[str, Any]) -> bool:
        return ComplianceAlerter.event_source(event=event) == "aws:s3"

    def fetch(self, event: Dict[str, Any]) -> Audit:
        return AuditFetcher().fetch_audit(self.config.get_report_s3_client(), event)

    def analyse(self, audit: Audit) -> Set[Finding]:
        return AuditAnalyser().analyse(self.logger, audit, self.config)

    def build_audit_report_findings(self, event: Dict[str, Any]) -> Set[Finding]:
        return self.analyse(self.fetch(event))

    def build_sns_event_findings(self, event: Dict[str, Any]) -> Set[Finding]:
        findings: Set[Finding] = set()
        ci_account_id = self.config.get_ci_account_id()
        for record in event["Records"]:
            message = json.loads(record["Sns"]["Message"])
            detail_type = message.get("detailType") or message.get("detail-type")
            if "approval" in message:
                self.logger.info("Manual approval event received")
                findings.add(CodePipeline().create_approval_finding(message, ci_account_id))
            elif detail_type == CodePipeline.Type:
                findings.add(CodePipeline().create_finding(message))
            elif detail_type == CodeBuild.Type:
                findings.add(CodeBuild().create_finding(message))
            elif detail_type == GuardDuty.Type:
                findings.add(GuardDuty(self.config).create_finding(message))
            elif detail_type == GrantUserAccessLambda.Type:
                findings.add(GrantUserAccessLambda().create_finding(message))
            elif detail_type == AwsHealth.Type and AwsHealth().is_a_target_event_type(message):
                findings.add(AwsHealth().create_finding(message))
            else:
                self.logger.warning(f"Received unknown event with detailType '{detail_type}'. Ignoring...")
                self.logger.info(f"Full event: {json.dumps(message)}")

        return findings

    def build_pagerduty_payloads(self, event: Dict[str, Any]) -> Set[PagerDutyPayload]:
        payloads: Set[PagerDutyPayload] = set()
        for record in event["Records"]:
            message = json.loads(record["Sns"]["Message"])
            detail_type = message.get("detailType") or message.get("detail-type")
            if detail_type == AwsHealth.Type and AwsHealth().is_a_target_event_type(message):
                payloads.add(AwsHealth().create_pagerduty_event_payload(message))
            else:
                # A "warning" log level will get unnecessarily noisy.
                logging.getLogger(__name__).debug(
                    f"PagerDuty notification is not supported for event with detailType '{detail_type}'. Ignoring..."
                )
        return payloads

    def send(self, notifier: Notifier[N, P], payloads: Set[P]) -> None:
        notifier.send(notifier.apply_mappings(notifier.apply_filters(payloads)))
