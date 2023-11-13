from json import dumps
from logging import Logger
from typing import Any, Dict, Optional, Sequence, Set

from src.compliance.action_describer import ActionDescriber, BriefActionDescriber, DetailedActionDescriber
from src.compliance.analyser import Analyser
from src.data.account import Account
from src.data.action import Action
from src.data.audit import Audit
from src.data.finding import Finding
from src.data.severity import Severity


class ActionableReportCompliance(Analyser):
    action: ActionDescriber

    def __init__(self, logger: Logger, item_type: str, item: str):
        self.item = item
        self.action = BriefActionDescriber()
        super().__init__(logger=logger, item_type=item_type)

    def analyse(self, audit: Audit) -> Set[Finding]:
        return {
            self._account_findings(
                account=Account.from_dict(report["account"]),
                region_name=report["region"],
                actions=[Action.from_dict(action) for action in report["results"]["enforcement_actions"]],
                results=report["results"],
            )
            for report in audit.report
        }

    def _account_findings(
        self, account: Account, region_name: str, actions: Sequence[Action], results: Dict[str, Any]
    ) -> Finding:
        return Finding(
            account=account,
            region_name=region_name,
            compliance_item_type=self.item_type,
            item=self.item,
            description=self._build_description(actions, results),
            findings=self._build_findings(actions),
            severity=self._build_severity(actions),
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

    def _build_severity(self, actions: Sequence[Action]) -> Severity:
        if self._any_failed(actions) or self._none_applied(actions):
            return Severity.HIGH
        else:
            return Severity.LOW

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
    def __init__(self, logger: Logger, item_type: str, item: str):
        super().__init__(item_type=item_type, item=item, logger=logger)
        self.action = DetailedActionDescriber()

    def _build_description(self, actions: Sequence[Action], results: Dict[str, Any]) -> Optional[str]:
        results.pop("enforcement_actions")
        return f"{self._determine_compliance_status(actions)}\n```{dumps(results, indent=4)}```"
