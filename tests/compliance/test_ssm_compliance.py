from logging import getLogger
from src.compliance.ssm_compliance import SSMCompliance

from tests.fixtures.ssm_compliance import (
    ssm_audit_report,
    ssm_audit_report_non_compliant_s3_config_items,
    ssm_audit_report_non_compliant_max_session_duration_shell_profile,
)
from tests.test_types_generator import account, create_audit, finding


acc_1 = account("111222333444", "account-1")

FINDINGS_DESCRIPTION = (
    "SSM config SSM-SessionManagerRunShell is not compliant, which may limit "
    "MDTP's ability to log/audit connection sessions to EC2 nodes"
)


def test_analyse_ssm_document_audit_compliant() -> None:
    audit = create_audit(type="audit_ssm_document.json", report=ssm_audit_report)
    assert SSMCompliance(getLogger()).analyse(audit) == {
        finding(
            account=acc_1,
            compliance_item_type="ssm_document",
            item="SSM-SessionManagerRunShell",
            findings=set(),
            description=FINDINGS_DESCRIPTION,
        )
    }


def test_analyse_ssm_document_audit_non_compliant_on_s3_config_items() -> None:
    audit = create_audit(type="audit_ssm_document.json", report=ssm_audit_report_non_compliant_s3_config_items)
    assert SSMCompliance(getLogger()).analyse(audit) == {
        finding(
            account=acc_1,
            compliance_item_type="ssm_document",
            item="SSM-SessionManagerRunShell",
            findings={
                "S3 bucket name should be mdtp-ssm-session-manager-audit-logs",
                "S3 encryption should be enabled",
            },
            description=FINDINGS_DESCRIPTION,
        )
    }


def test_analyse_ssm_document_audit_non_compliant_on_session_duration_and_shell_profile() -> None:
    audit = create_audit(
        type="audit_ssm_document.json", report=ssm_audit_report_non_compliant_max_session_duration_shell_profile
    )
    assert SSMCompliance(getLogger()).analyse(audit) == {
        finding(
            account=acc_1,
            compliance_item_type="ssm_document",
            item="SSM-SessionManagerRunShell",
            findings={
                "maxSessionDuration should be less than or equal to 120 mins",
                "shellProfile should match expected config",
            },
            description=FINDINGS_DESCRIPTION,
        )
    }
