from typing import Set

from src.data.audit import Audit
from src.data.findings import Findings
from src.compliance.actionable_report_compliance import DetailedActionableReportCompliance
from src.compliance.analyser import Analyser


class VpcCompliance(Analyser):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return DetailedActionableReportCompliance("vpc", "VPC flow logs").analyse(audit)
