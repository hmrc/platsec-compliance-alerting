from logging import getLogger
from src.compliance.ssm_compliance import SSMCompliance

from tests.fixtures.ssm_compliance import ssm_audit_report
from tests.test_types_generator import account, create_audit, findings


acc_1 = account("111222333444", "account-1")
acc_2 = account("787878787878", "account-2")

finding_1 = findings(
    account=acc_1,
    compliance_item_type="ssm_document",
    item="SSM-SessionManagerRunShell",
    findings={"compliant: False"},
    description="SSM Document SSM-SessionManagerRunShell does not match the expected config",
)


def test_analyse_ssm_document_audit() -> None:
    audit = create_audit(type="audit_ssm_document.json", report=ssm_audit_report)
    assert SSMCompliance(getLogger()).analyse(audit) == {finding_1}
