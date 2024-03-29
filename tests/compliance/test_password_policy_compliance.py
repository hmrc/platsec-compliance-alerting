from logging import getLogger
from typing import Any, Dict, Optional, Sequence, Set

from src.data.severity import Severity
from tests.test_types_generator import create_account, create_audit, finding

from src.compliance.actionable_report_compliance import DetailedActionableReportCompliance
from src.data.account import Account
from src.data.audit import Audit
from src.data.finding import Finding


def test_empty_findings_when_audit_has_no_actions() -> None:
    acc = create_account()
    audit = _password_policy_audit(acc)
    prettified_results = '```{\n    "some_results": "some_value"\n}```'
    expected_description = f"password policy compliance is met\n{prettified_results}"
    assert DetailedActionableReportCompliance(getLogger(), "password_policy", "password policy").analyse(
        audit
    ) == _findings(Severity.LOW, acc, expected_description)


def test_vpc_compliance_not_met_when_audit_has_actions() -> None:
    acc = create_account()
    audit = _password_policy_audit(
        acc, actions=[{"description": "a"}, {"description": "b", "details": {"some_details": "bla"}}]
    )
    prettified_results = '```{\n    "some_results": "some_value"\n}```'
    expected_description = f"password policy compliance is not met\n{prettified_results}"
    expected_actions = {'required: a\nb\n```{\n    "some_details": "bla"\n}```'}
    expected_findings = _findings(Severity.HIGH, acc, expected_description, expected_actions)
    assert (
        DetailedActionableReportCompliance(getLogger(), "password_policy", "password policy").analyse(audit)
        == expected_findings
    )


def test_vpc_compliance_enforcement_success_when_all_actions_applied() -> None:
    acc = create_account()
    audit = _password_policy_audit(
        acc,
        actions=[
            {"description": "a", "status": "applied", "details": {"some_key": 1}},
            {"description": "b", "status": "applied"},
        ],
    )
    prettified_results = '```{\n    "some_results": "some_value"\n}```'
    expected_description = f"password policy compliance enforcement success\n{prettified_results}"
    expected_actions = {'applied: a\n```{\n    "some_key": 1\n}```\nb'}
    expected_findings = _findings(Severity.LOW, acc, expected_description, expected_actions)
    assert expected_findings == DetailedActionableReportCompliance(
        getLogger(), "password_policy", "password policy"
    ).analyse(audit)


def test_vpc_compliance_enforcement_failure_when_any_action_failed() -> None:
    acc = create_account()
    audit = _password_policy_audit(
        acc,
        actions=[
            {"description": "a", "status": "applied"},
            {"description": "b", "details": {"a_key": 42}, "status": "failed: boom"},
        ],
    )
    prettified_results = '```{\n    "some_results": "some_value"\n}```'
    expected_description = f"password policy compliance enforcement failure\n{prettified_results}"
    expected_actions = {'applied: a\nfailed: b\n```{\n    "a_key": 42\n}```\nerror: boom'}
    expected_findings = _findings(Severity.HIGH, acc, expected_description, expected_actions)
    assert (
        DetailedActionableReportCompliance(getLogger(), "password_policy", "password policy").analyse(audit)
        == expected_findings
    )


def _password_policy_audit(acc: Account, actions: Optional[Sequence[Dict[str, Any]]] = None) -> Audit:
    return create_audit(
        type="password_policy",
        report=[
            {
                "account": {"identifier": acc.identifier, "name": acc.name},
                "region": "test-region-name",
                "results": {"some_results": "some_value", "enforcement_actions": actions or []},
            }
        ],
    )


def _findings(
    severity: Severity, acc: Account, desc: Optional[str] = None, find: Optional[Set[str]] = None
) -> Set[Finding]:
    return {
        finding(
            severity=severity,
            account=acc,
            compliance_item_type="password_policy",
            item="password policy",
            findings=find,
            description=desc,
        )
    }
