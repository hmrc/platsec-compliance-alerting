from typing import Set

from src.compliance.s3_compliance import S3Compliance
from src.compliance.github_compliance import GithubCompliance
from src.config.config import Config
from src.data.audit import Audit
from src.data.notification import Notification
from src.data.exceptions import UnsupportedAuditException


class AuditAnalyser:
    @staticmethod
    def analyse(audit: Audit, config: Config) -> Set[Notification]:
        try:
            # This is where we need to check whether to do github or s3 compliance
            githubKey = config.get_github_audit_report_key()
            if audit.type == githubKey:
                return {githubKey: GithubCompliance}[audit.type]().analyse(audit)

            return {config.get_s3_audit_report_key(): S3Compliance}[audit.type]().analyse(audit)
        except KeyError:
            raise UnsupportedAuditException(audit.type)
