from os import environ

from unittest import TestCase
from unittest.mock import patch

from tests.fixtures.s3_compliance import s3_report
from tests.test_types_generator import account, findings

from src.config.config import Config
from src.data.audit import Audit
from src.compliance.s3_compliance import S3Compliance

mischievous_bucket_finding = findings(
    account=account("111222333444", "another-account"),
    compliance_item_type="s3_bucket",
    item="mischievous-bucket",
    findings={
        "bucket should have a resource policy with secure transport enforced",
        "bucket should have logging enabled",
        "bucket should have tags for expiry and sensitivity",
        "bucket should have a resource policy with a default deny action",
        "bucket should not allow public access",
        "bucket kms key should have rotation enabled",
    },
)
bad_bucket_finding = findings(
    account=account("555666777444", "an-account"),
    compliance_item_type="s3_bucket",
    item="bad-bucket",
    findings={
        "bucket should be encrypted",
        "bucket should have tags for expiry and sensitivity",
        "bucket should have logging enabled",
    },
)
good_bucket_finding = findings(
    account=account("555666777444", "an-account"),
    compliance_item_type="s3_bucket",
    item="good-bucket",
    findings=set(),
)
good_bucket_high_sensitivity_finding = findings(
    account=account("999999999999", "another-account-2"),
    compliance_item_type="s3_bucket",
    item="good-bucket-high-sensitivity",
    findings=set(),
)
bad_bucket_low_sensitivity_finding = findings(
    account=account("555666777444", "an-account"),
    compliance_item_type="s3_bucket",
    item="bad-bucket-low-sensitivity",
    findings={
        "bucket should be encrypted",
        "bucket should have logging enabled",
        "bucket should not allow public access",
        "bucket should have tags for expiry and sensitivity",
    },
)
an_account_finding = findings(
    account=account("555666777444", "an-account"),
    compliance_item_type="s3_compliance_summary",
    description="Account an-account has S3 buckets that do not comply with the policy",
    item="an-account",
    findings={"Here is a detailed S3 audit report: the-dashboard"},
)
another_account_finding = findings(
    account=account("111222333444", "another-account"),
    compliance_item_type="s3_compliance_summary",
    description="Account another-account has S3 buckets that do not comply with the policy",
    item="another-account",
    findings={"Here is a detailed S3 audit report: the-dashboard"},
)

s3_compliance = S3Compliance(Config())


@patch.dict(environ, {"AUDIT_REPORT_DASHBOARD_URL": "the-dashboard"}, clear=True)
class TestS3Compliance(TestCase):
    def test_analyse_s3_audit(self) -> None:
        self.maxDiff = None
        audit = Audit(type="s3", report=s3_report)
        notifications = s3_compliance.analyse(audit)
        assert len(notifications) == 7
        assert mischievous_bucket_finding in notifications
        assert bad_bucket_finding in notifications
        assert good_bucket_finding in notifications
        assert good_bucket_high_sensitivity_finding in notifications
        assert bad_bucket_low_sensitivity_finding in notifications
        assert an_account_finding in notifications
        assert another_account_finding in notifications
