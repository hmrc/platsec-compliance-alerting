from typing import Any, Dict, Optional, Sequence, Set

from src.compliance.action_describer import ActionDescriber, BriefActionDescriber, DetailedActionDescriber
from src.compliance.analyser import Analyser
from src.data.account import Account
from src.data.action import Action
from src.data.audit import Audit
from src.data.findings import Findings


class ActionableReportCompliance(Analyser):
    action: ActionDescriber

    def __init__(self, item_type: str, item: str):
        self.item_type = item_type
        self.item = item
        self.action = BriefActionDescriber()

    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._account_findings(
                account=Account.from_dict(report["account"]),
                actions=[Action.from_dict(action) for action in report["results"]["enforcement_actions"]],
                results=report["results"],
            )
            for report in audit.report
        }

    def _account_findings(self, account: Account, actions: Sequence[Action], results: Dict[str, Any]) -> Findings:
        return Findings(
            account=account,
            compliance_item_type=self.item_type,
            item=self.item,
            description=self._build_description(actions, results),
            findings=self._build_findings(actions),
        )

    def _build_description(self, actions: Sequence[Action], results: Dict[str, Any]) -> Optional[str]:
        return self._determine_compliance_status(actions)

    def _determine_compliance_status(self, actions: Sequence[Action]) -> str:
        if not actions:
            return f"{self.item} compliance is met"
        if self._any_failed(actions):
            return f"{self.item} compliance enforcement failure"
        if self._all_applied(actions):
            return f"{self.item} compliance enforcement success"
        return f"{self.item} compliance is not met"

    def _build_findings(self, actions: Sequence[Action]) -> Optional[Set[str]]:
        if self._none_applied(actions):
            return {f"required: {self.action.describe(actions)}"}
        if self._all_applied(actions):
            return {f"applied: {self.action.describe(actions)}"}
        if self._any_failed(actions):
            return {f"applied: {self.action.describe_applied(actions)}\nfailed: {self.action.describe_failed(actions)}"}
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


class DetailedActionableReportCompliance(ActionableReportCompliance):
    def __init__(self, item_type: str, item: str):
        super().__init__(item_type=item_type, item=item)
        self.action = DetailedActionDescriber()

    def _build_description(self, actions: Sequence[Action], results: Dict[str, Any]) -> Optional[str]:
        results.pop("enforcement_actions")
        return f"{self._determine_compliance_status(actions)}\ndetails: {results}"
