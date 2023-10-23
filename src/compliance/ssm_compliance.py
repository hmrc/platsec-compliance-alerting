from logging import Logger
from typing import Set
from src.data.account import Account

from src.data.audit import Audit
from src.data.findings import Findings
from src.compliance.analyser import Analyser


class SSMCompliance(Analyser):
    def __init__(self, logger: Logger):
        self.item_type = "ssm_document"
        super().__init__(logger, item_type=self.item_type)

    def analyse(self, audit: Audit) -> Set[Findings]:
        findings = set()
        for sub_report in audit.report:
            for document in sub_report["results"]["documents"]:
                findings_messages = set()
                for key, value in document["compliancy"].items():
                    if not value["compliant"]:
                        findings_messages.add(value["message"])
                findings.add(
                    Findings(
                        compliance_item_type=self.item_type,
                        account=Account.from_dict(sub_report["account"]),
                        region_name=sub_report["region"],
                        item=document["name"],
                        findings=findings_messages,
                        description=f"SSM Document {document['name']} does not match the expected config",
                    )
                )
        return findings
