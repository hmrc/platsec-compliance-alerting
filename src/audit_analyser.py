from typing import Set, Dict, Type

from src.compliance.iam_compliance import IamCompliance
from src.compliance.s3_compliance import S3Compliance
from src.compliance.github_compliance import GithubCompliance
from src.compliance.vpc_compliance import VpcCompliance
from src.compliance.analyser_interface import AnalyserInterface
from src.config.config import Config
from src.data.audit import Audit
from src.data.findings import Findings
from src.data.exceptions import UnsupportedAuditException


class AuditAnalyser:
    @staticmethod
    def analyse(audit: Audit, config: Config) -> Set[Findings]:
        try:
            config_map: Dict[str, Type[AnalyserInterface]] = {
                config.get_github_audit_report_key(): GithubCompliance,
                config.get_s3_audit_report_key(): S3Compliance,
                config.get_iam_audit_report_key(): IamCompliance,
                config.get_vpc_audit_report_key(): VpcCompliance,
            }
            return config_map[audit.type]().analyse(audit)
        except KeyError:
            raise UnsupportedAuditException(audit.type)
