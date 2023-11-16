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
    compliance_alerter.send(
        notifier=SlackNotifier(config=compliance_alerter.config),
        payloads=compliance_alerter.build_findings(event=event),
    )
    compliance_alerter.send(
        notifier=PagerDutyNotifier(config=compliance_alerter.config),
        payloads=compliance_alerter.build_pagerduty_payloads(event=event),
    )


class ComplianceAlerter:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = Config.configure_logging()

    @staticmethod
    def is_sns_event(event: Dict[str, Any]) -> bool:
        return "EventSource" in event.get("Records", [{}])[0] and event["Records"][0].get("EventSource") == "aws:sns"

    def fetch(self, event: Dict[str, Any]) -> Audit:
        return AuditFetcher().fetch_audit(self.config.get_report_s3_client(), event)

    def analyse(self, audit: Audit) -> Set[Finding]:
        return AuditAnalyser().analyse(self.logger, audit, self.config)

    def build_findings(self, event: Dict[str, Any]) -> Set[Finding]:
        # findings: Set[Payload] 
        findings = (
            self.build_sns_event_findings(event)
            if ComplianceAlerter.is_sns_event(event)
            else self.analyse(self.fetch(event))
        )
        return findings

    def build_sns_event_findings(self, events: Dict[str, Any]) -> Set[Finding]:
        findings: Set[Finding] = set()
        for record in events["Records"]:
            message = json.loads(record["Sns"]["Message"])
            type = message.get("detailType") or message.get("detail-type")
            if type == CodePipeline.Type:
                findings.add(CodePipeline().create_finding(message))
            elif type == CodeBuild.Type:
                findings.add(CodeBuild().create_finding(message))
            elif type == GuardDuty.Type:
                findings.add(GuardDuty(self.config).create_finding(message))
            elif type == GrantUserAccessLambda.Type:
                findings.add(GrantUserAccessLambda().create_finding(message))
            elif type == AwsHealth.Type:
                findings.add(AwsHealth().create_finding(message))
            else:
                logging.getLogger(__name__).warning(f"Received unknown event with detailType '{type}'. Ignoring...")
        return findings

    def build_pagerduty_payloads(self, event: Dict[str, Any]) -> Set[PagerDutyPayload]:
        payloads: Set[PagerDutyPayload] = set()
        for record in event["Records"]:
            message = json.loads(record["Sns"]["Message"])
            type = message.get("detailType") or message.get("detail-type")
            if type == AwsHealth.Type:
                payloads.add(AwsHealth().create_pagerduty_event_payload(message))
            else:
                # A "warning" log level will get unnecessarily noisy.
                logging.getLogger(__name__).debug(
                    f"PagerDuty notification is not supported for event with detailType '{type}'. Ignoring..."
                )
        return payloads

    def send(self, notifier: Notifier[N, P], payloads: Set[P]) -> None:
        notifier.send(notifier.apply_mappings(notifier.apply_filters(payloads)))
