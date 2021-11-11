from typing import Any, Dict, Set

from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings
from src.compliance.analyser_interface import AnalyserInterface


class VpcCompliance(AnalyserInterface):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._check_vpc_rules(report["account"], vpc)
            for report in audit.report
            for vpc in report["results"]["vpcs"]
        }

    def _check_vpc_rules(self, account: Dict[str, str], vpc: Dict[str, Any]) -> Findings:
        return Findings(
            account=Account.from_dict(account),
            compliance_item_type="vpc",
            item=vpc["id"],
            findings=set(),
        )
