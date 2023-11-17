from logging import Logger
from typing import Set
from src.data.account import Account

from src.data.audit import Audit
from src.data.finding import Finding
from src.compliance.analyser import Analyser


class SSMCompliance(Analyser):
    def __init__(self, logger: Logger):
        self.item_type = "ssm_document"
        super().__init__(logger, item_type=self.item_type)

    def analyse(self, audit: Audit) -> Set[Finding]:
        findings = set()
        for sub_report in audit.report:
            for document in sub_report["results"]["documents"]:
                findings_messages = set()
                for key, value in document["compliancy"].items():
                    if not value["compliant"]:
                        findings_messages.add(value["message"])
                findings.add(
                    Finding(
                        compliance_item_type=self.item_type,
                        account=Account.from_dict(sub_report["account"]),
                        region_name=sub_report["region"],
                        item=document["name"],
                        findings=findings_messages,
                        description=(
                            f"SSM config {document['name']} is not compliant, which may limit "
                            "MDTP's ability to log/audit connection sessions to EC2 nodes"
                        ),
                    )
                )
        return findings
