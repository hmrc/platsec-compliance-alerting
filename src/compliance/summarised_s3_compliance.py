from typing import Set

from src.config.config import Config
from src.data.finding import Finding


class SummarisedS3Compliance:
    def __init__(self, config: Config) -> None:
        self.config = config

    def summarise(self, findings: Set[Finding]) -> Set[Finding]:
        return {
            Finding(
                account=finding.account,
                region_name=finding.region_name,
                compliance_item_type="s3_compliance_summary",
                description=f"Account {finding.account_name} has S3 buckets that do not comply with the policy",
                item=finding.account_name,
                findings={f"Here is a detailed S3 audit report: {self.config.get_audit_report_dashboard_url()}"},
            )
            for finding in findings
            if finding.findings
        }
