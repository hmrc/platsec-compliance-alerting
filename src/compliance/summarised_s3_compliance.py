from typing import Set

from src.config.config import Config
from src.data.findings import Findings


class SummarisedS3Compliance:
    def __init__(self, config: Config) -> None:
        self.config = config

    def summarise(self, findings: Set[Findings]) -> Set[Findings]:
        return {
            Findings(
                account=finding.account,
                compliance_item_type="s3_compliance_summary",
                description=f"Here is a detailed S3 audit report: {self.config.get_audit_report_dashboard_url()}",
                item=finding.account_name,
                findings={f"Account {finding.account_name} has S3 buckets that do not comply with the policy"},
            )
            for finding in findings
            if finding.findings
        }
