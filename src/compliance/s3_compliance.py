from logging import Logger
from typing import Any, Dict, Set

from src.config.config import Config
from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings
from src.compliance.analyser import Analyser
from src.compliance.summarised_s3_compliance import SummarisedS3Compliance


class S3Compliance(Analyser):
    def __init__(self, logger: Logger, config: Config) -> None:
        self.config = config
        super().__init__(logger=logger, item_type="s3_bucket")

    def analyse(self, audit: Audit) -> Set[Findings]:
        findings = {
            self._check_bucket_compliancy(report["account"], report["region"], bucket)
            for report in audit.report
            for bucket in report["results"]["buckets"]
        }
        findings.update(SummarisedS3Compliance(self.config).summarise(findings))
        return findings

    def _check_bucket_compliancy(self, account: Dict[str, str], region_name: str, bucket: Dict[str, Any]) -> Findings:
        findings = set()
        for key in bucket["compliancy"]:
            if not bucket["compliancy"][key]["compliant"]:
                if (
                    key == "logging"
                    and "skipped" in bucket["compliancy"]["logging"]
                    and bucket["compliancy"]["logging"]["skipped"]
                ):
                    continue
                findings.add(bucket["compliancy"][key]["message"])

        return Findings(
            account=Account.from_dict(account),
            region_name=region_name,
            compliance_item_type=self.item_type,
            item=bucket["name"],
            findings=findings,
        )
