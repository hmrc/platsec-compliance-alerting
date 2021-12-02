from typing import Optional, Sequence, Set

from src.data.action import Action
from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings
from src.compliance.analyser import Analyser


class ActionableReportCompliance(Analyser):
    def __init__(self, item_type: str, item: str):
        self.item_type = item_type
        self.item = item

    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._account_findings(
                account=Account.from_dict(report["account"]),
                actions=[Action.from_dict(action) for action in report["results"]["enforcement_actions"]],
            )
            for report in audit.report
        }

    def _account_findings(self, account: Account, actions: Sequence[Action]) -> Findings:
        return Findings(
            account=account,
            compliance_item_type=self.item_type,
            item=self.item,
            description=self._build_description(actions),
            findings=self._build_findings(actions),
        )

    def _build_description(self, actions: Sequence[Action]) -> Optional[str]:
        if not actions:
            return f"{self.item} compliance is met"
        if self._any_failed(actions):
            return f"{self.item} compliance enforcement failure"
        if self._all_applied(actions):
            return f"{self.item} compliance enforcement success"
        return f"{self.item} compliance is not met"

    def _build_findings(self, actions: Sequence[Action]) -> Optional[Set[str]]:
        if self._none_applied(actions):
            return {f"required: {self._describe(actions)}"}
        if self._all_applied(actions):
            return {f"applied: {self._describe(actions)}"}
        if self._any_failed(actions):
            return {f"applied: {self._describe_applied(actions)}\nfailed: {self._describe_failed(actions)}"}
        return None

    @staticmethod
    def _none_applied(actions: Sequence[Action]) -> bool:
        return bool(actions) and all([a.is_not_applied() for a in actions])

    @staticmethod
    def _all_applied(actions: Sequence[Action]) -> bool:
        return bool(actions) and all([a.is_applied() for a in actions])

    @staticmethod
    def _any_failed(actions: Sequence[Action]) -> bool:
        return bool(actions) and any([a.has_failed() for a in actions])

    @staticmethod
    def _describe(actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(a.description for a in actions)

    @staticmethod
    def _describe_applied(actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(a.description for a in actions if a.is_applied())

    @staticmethod
    def _describe_failed(actions: Sequence[Action]) -> Sequence[str]:
        return ", ".join(f"{a.description} ({a.reason()})" for a in actions if a.has_failed())
