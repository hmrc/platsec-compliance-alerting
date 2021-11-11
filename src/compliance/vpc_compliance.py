from typing import Optional, Sequence, Set

from src.data.action import Action
from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings
from src.compliance.analyser_interface import AnalyserInterface


class VpcCompliance(AnalyserInterface):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._get_account_findings(
                account=Account.from_dict(report["account"]),
                actions=[Action.from_dict(action) for action in report["results"]["enforcement_actions"]],
            )
            for report in audit.report
        }

    @staticmethod
    def _get_account_findings(account: Account, actions: Sequence[Action]) -> Findings:
        return Findings(
            account=account,
            compliance_item_type="vpc",
            item="VPC flow logs",
            findings=VpcCompliance._build_findings(actions),
            description=VpcCompliance._build_description(actions),
        )

    @staticmethod
    def _build_description(actions: Sequence[Action]) -> Optional[str]:
        return "VPC compliance not met" if actions else None

    @staticmethod
    def _build_findings(actions: Sequence[Action]) -> Optional[Set[str]]:
        return {f"actions required: {', '.join(a.description for a in actions)}"} if actions else None
