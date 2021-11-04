from typing import Set, Dict, Type

from src.compliance.s3_compliance import S3Compliance
from src.compliance.github_compliance import GithubCompliance
from src.compliance.analyser_interface import AnalyserInterface
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.data.exceptions import UnsupportedAuditException


class AuditAnalyser:
    @staticmethod
    def analyse(audit: Audit, config: Config) -> Set[Findings]:
        try:
            configMap: Dict[str, Type[AnalyserInterface]] = {
                config.get_github_audit_report_key(): GithubCompliance,
                config.get_s3_audit_report_key(): S3Compliance,
            }

            return configMap[audit.type]().analyse(audit)
        except KeyError:
            raise UnsupportedAuditException(audit.type)
