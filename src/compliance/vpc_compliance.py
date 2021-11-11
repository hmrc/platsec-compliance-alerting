from typing import Sequence, Set

from src.data.action import Action
from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings
from src.compliance.analyser_interface import AnalyserInterface


class VpcCompliance(AnalyserInterface):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._get_findings(
                account=Account.from_dict(report["account"]),
                actions=[Action(**action) for action in report["results"]["enforcement_actions"]],
            )
            for report in audit.report
        }

    def _get_findings(self, account: Account, actions: Sequence[Action]) -> Findings:
        return Findings(
            account=account,
            compliance_item_type="vpc",
            item="VPC flow logs",
            findings=None if not actions else set(),
        )
