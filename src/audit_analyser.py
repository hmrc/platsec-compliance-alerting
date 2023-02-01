from logging import Logger
from typing import Set, Dict

from src.compliance.actionable_report_compliance import ActionableReportCompliance
from src.compliance.analyser import Analyser
from src.compliance.ec2_compliance import Ec2Compliance
from src.compliance.iam_compliance import IamCompliance
from src.compliance.s3_compliance import S3Compliance
from src.compliance.github_compliance import GithubCompliance
from src.compliance.github_webhook_compliance import GithubWebhookCompliance
from src.compliance.vpc_compliance import VpcCompliance
from src.compliance.vpc_peering_compliance import VpcPeeringCompliance
from src.compliance.password_policy_compliance import PasswordPolicyCompliance
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.data.exceptions import UnsupportedAuditException


class AuditAnalyser:
    @staticmethod
    def analyse(logger: Logger, audit: Audit, config: Config) -> Set[Findings]:
        for audit_key, audit_analyser in AuditAnalyser.config_map(logger, config).items():
            if audit.type.startswith(audit_key):
                return audit_analyser.analyse(audit)

        if audit.type in config.get_ignorable_report_keys():
            logger.warning(f"Ignoring unsupported key '{audit.type}' as it is present in ignorable_report_keys config")
            return set()
        else:
            raise UnsupportedAuditException(audit.type)

    @staticmethod
    def config_map(logger: Logger, config: Config) -> Dict[str, Analyser]:
        return {
            config.get_github_audit_report_key(): GithubCompliance(logger),
            config.get_github_webhook_report_key(): GithubWebhookCompliance(logger, config),
            config.get_s3_audit_report_key(): S3Compliance(logger, config),
            config.get_iam_audit_report_key(): IamCompliance(logger),
            config.get_vpc_audit_report_key(): VpcCompliance(logger),
            config.get_password_policy_audit_report_key(): PasswordPolicyCompliance(logger),
            config.get_vpc_peering_audit_report_key(): VpcPeeringCompliance(logger),
            config.get_ec2_audit_report_key(): Ec2Compliance(logger),
            config.get_vpc_resolver_audit_report_key(): ActionableReportCompliance(
                logger=logger, item_type="vpc_dns_log", item="vpc dns log"
            ),
            config.get_public_query_audit_report_key(): ActionableReportCompliance(
                logger=logger, item_type="public_query_log", item="public query log"
            ),
        }
