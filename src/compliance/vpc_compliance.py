from typing import Optional, Sequence, Set

from src.data.action import Action
from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings
from src.compliance.analyser_interface import AnalyserInterface


ENFORCEMENT_SUCCESS = "VPC compliance enforcement success"
COMPLIANT = "VPC compliance is met"
NOT_COMPLIANT = "VPC compliance is not met"


class VpcCompliance(AnalyserInterface):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._get_account_findings(
                account=Account.from_dict(report["account"]),
                actions=[Action.from_dict(action) for action in report["results"]["enforcement_actions"]],
            )
            for report in audit.report
        }

    def _get_account_findings(self, account: Account, actions: Sequence[Action]) -> Findings:
        return Findings(
            account=account,
            compliance_item_type="vpc",
            item="VPC flow logs",
            description=self._build_description(actions),
            findings=self._build_findings(actions),
        )

    def _build_description(self, actions: Sequence[Action]) -> Optional[str]:
        return COMPLIANT if not actions else ENFORCEMENT_SUCCESS if self._all_applied(actions) else NOT_COMPLIANT

    def _build_findings(self, actions: Sequence[Action]) -> Optional[Set[str]]:
        state = "applied" if self._all_applied(actions) else "required"
        return {f"actions {state}: {self._get_descriptions(actions)}"} if actions else None

    @staticmethod
    def _all_applied(actions: Sequence[Action]) -> bool:
        return all([a.is_applied() for a in actions])

    @staticmethod
    def _get_descriptions(actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(a.description for a in actions)
