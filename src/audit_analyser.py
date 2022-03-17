from typing import Set, Dict

from src.compliance.analyser import Analyser
from src.compliance.iam_compliance import IamCompliance
from src.compliance.s3_compliance import S3Compliance
from src.compliance.github_compliance import GithubCompliance
from src.compliance.github_webhook_compliance import GithubWebhookCompliance
from src.compliance.vpc_compliance import VpcCompliance
from src.compliance.password_policy_compliance import PasswordPolicyCompliance
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.data.exceptions import UnsupportedAuditException


class AuditAnalyser:
    @staticmethod
    def analyse(audit: Audit, config: Config) -> Set[Findings]:
        config_map: Dict[str, Analyser] = {
            config.get_github_audit_report_key(): GithubCompliance(),
            config.get_github_webhook_report_key(): GithubWebhookCompliance(config),
            config.get_s3_audit_report_key(): S3Compliance(config),
            config.get_iam_audit_report_key(): IamCompliance(),
            config.get_vpc_audit_report_key(): VpcCompliance(),
            config.get_password_policy_audit_report_key(): PasswordPolicyCompliance(),
        }

        for audit_key, audit_analyser in config_map.items():
            if audit.type.startswith(audit_key):
                return audit_analyser.analyse(audit)

        raise UnsupportedAuditException(audit.type)
