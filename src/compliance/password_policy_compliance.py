from logging import Logger
from typing import Set

from src.data.audit import Audit
from src.data.findings import Findings
from src.compliance.actionable_report_compliance import DetailedActionableReportCompliance
from src.compliance.analyser import Analyser


class PasswordPolicyCompliance(Analyser):
    def analyse(self, logger: Logger, audit: Audit) -> Set[Findings]:
        return DetailedActionableReportCompliance("password_policy", "password policy").analyse(logger, audit)
