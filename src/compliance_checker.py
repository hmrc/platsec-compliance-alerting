from typing import Set

from src.compliance.s3_compliance import S3Compliance
from src.config.config import Config
from src.data.audit import Audit
from src.data.notification import Notification
from src.data.exceptions import UnsupportedAuditException


class ComplianceChecker:
    @staticmethod
    def check(audit: Audit, config: Config) -> Set[Notification]:
        try:
            return {config.get_s3_audit_report_key(): S3Compliance}[audit.type]().check(audit)
        except KeyError:
            raise UnsupportedAuditException(audit.type)
