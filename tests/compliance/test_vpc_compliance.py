from logging import getLogger
from typing import Any, Dict, Optional, Sequence, Set

from tests.test_types_generator import create_account, create_audit, findings

from src.compliance.vpc_compliance import VpcCompliance
from src.data.account import Account
from src.data.audit import Audit
from src.data.findings import Findings


def test_empty_findings_when_audit_has_no_actions() -> None:
    acc = create_account()
    audit = _vpc_audit(acc)
    assert _vpc_findings(acc, "VPC flow logs compliance is met") == VpcCompliance(getLogger()).analyse(audit)


def test_vpc_compliance_not_met_when_audit_has_actions() -> None:
    acc = create_account()
    audit = _vpc_audit(acc, actions=[{"description": "a"}, {"description": "b", "details": "bla"}])
    expected_findings = _vpc_findings(acc, "VPC flow logs compliance is not met", {"required: a, b"})
    assert expected_findings == VpcCompliance(getLogger()).analyse(audit)


def test_vpc_compliance_enforcement_success_when_all_actions_applied() -> None:
    acc = create_account()
    audit = _vpc_audit(
        acc, actions=[{"description": "a", "status": "applied"}, {"description": "b", "status": "applied"}]
    )
    expected_findings = _vpc_findings(acc, "VPC flow logs compliance enforcement success", {"applied: a, b"})
    assert expected_findings == VpcCompliance(getLogger()).analyse(audit)


def test_vpc_compliance_enforcement_failure_when_any_action_failed() -> None:
    acc = create_account()
    audit = _vpc_audit(
        acc, actions=[{"description": "a", "status": "applied"}, {"description": "b", "status": "failed: boom"}]
    )
    expected_findings = _vpc_findings(
        acc, "VPC flow logs compliance enforcement failure", {"applied: a\nfailed: b (boom)"}
    )
    assert expected_findings == VpcCompliance(getLogger()).analyse(audit)


def _vpc_audit(acc: Account, actions: Optional[Sequence[Dict[str, Any]]] = None) -> Audit:
    return create_audit(
        type="audit_vpc_flow_logs",
        report=[
            {
                "account": {"identifier": acc.identifier, "name": acc.name},
                "results": {"enforcement_actions": actions or []},
            }
        ],
    )


def _vpc_findings(acc: Account, desc: Optional[str] = None, find: Optional[Set[str]] = None) -> Set[Findings]:
    return {findings(account=acc, compliance_item_type="vpc", item="VPC flow logs", findings=find, description=desc)}
