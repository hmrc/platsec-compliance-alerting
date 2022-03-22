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
        "bucket should not allow public access",
        "bucket should have a resource policy with a default deny action",
        "bucket should have data expiry tag",
        "bucket should have logging enabled",
        "bucket kms key should have rotation enabled",
    },
)
bad_bucket_finding = findings(
    account=account("555666777444", "an-account"),
    compliance_item_type="s3_bucket",
    item="bad-bucket",
    findings={
        "bucket should be encrypted",
        "bucket should have data sensitivity tag",
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
        "bucket should not allow public access",
        "bucket should have data expiry tag",
        "bucket should be encrypted",
        "bucket should have logging enabled",
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
    def test_key_is_enabled(self) -> None:
        self.assertTrue(s3_compliance._is_enabled("encryption", {"encryption": {"enabled": True}}))

    def test_key_is_disabled(self) -> None:
        self.assertFalse(s3_compliance._is_enabled("encryption", {"encryption": {"enabled": False}}))

    def test_key_bucket_missing(self) -> None:
        self.assertFalse(s3_compliance._is_enabled("encryption", {}))

    def test_key_undefined(self) -> None:
        self.assertFalse(s3_compliance._is_enabled("encryption", {"encryption": {}}))

    def test_bucket_has_tags(self) -> None:
        bucket = {"data_tagging": {"expiry": "not_unset", "sensitivity": "not_unset"}}
        self.assertTrue(s3_compliance._is_tagged("expiry", bucket))

    def test_bucket_has_one_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "unset", "sensitivity": "not_unset"}}
        self.assertFalse(s3_compliance._is_tagged("expiry", bucket))

    def test_bucket_has_one_other_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "not_unset", "sensitivity": "unset"}}
        self.assertFalse(s3_compliance._is_tagged("sensitivity", bucket))

    def test_bucket_has_one_missing_tag(self) -> None:
        self.assertFalse(s3_compliance._is_tagged("expiry", {"data_tagging": {"sensitivity": "unset"}}))

    def test_bucket_has_other_missing_tag(self) -> None:
        self.assertFalse(s3_compliance._is_tagged("sensitivity", {"data_tagging": {"expiry": "unset"}}))

    def test_bucket_has_expiry_tag_undefined(self) -> None:
        self.assertFalse(s3_compliance._is_tagged("expiry", {"data_tagging": {}}))

    def test_bucket_expiry_tag_bucket_missing(self) -> None:
        self.assertFalse(s3_compliance._is_tagged("expiry", {}))

    def test_bucket_has_sensitivity_tag_undefined(self) -> None:
        self.assertFalse(s3_compliance._is_tagged("sensitivity", {"data_tagging": {}}))

    def test_bucket_sensitivity_tag_bucket_missing(self) -> None:
        self.assertFalse(s3_compliance._is_tagged("sensitivity", {}))

    def test_bucket_has_secure_transport_unenforced(self) -> None:
        self.assertFalse(s3_compliance._is_enabled("secure_transport", {"secure_transport": {}}))

    def test_bucket_has_secure_transport_enforced(self) -> None:
        self.assertTrue(s3_compliance._is_enabled("secure_transport", {"secure_transport": {"enabled": True}}))

    def test_bucket_has_content_deny_unenforced(self) -> None:
        self.assertFalse(s3_compliance._is_enabled("content_deny", {"content_deny": {}}))

    def test_bucket_has_content_deny_enforced(self) -> None:
        self.assertTrue(s3_compliance._is_enabled("content_deny", {"content_deny": {"enabled": True}}))

    def test_bucket_has_logging_unenforced(self) -> None:
        self.assertFalse(s3_compliance._is_enabled("logging", {"logging": {}}))

    def test_bucket_has_logging_enforced(self) -> None:
        self.assertTrue(s3_compliance._is_enabled("logging", {"logging": {"enabled": True}}))

    def test_bucket_is_encrypted_with_cmk(self) -> None:
        self.assertTrue(s3_compliance._is_encrypted_with_cmk({"encryption": {"type": "cmk"}}))

    def test_bucket_is_not_encrypted_with_cmk(self) -> None:
        self.assertFalse(s3_compliance._is_encrypted_with_cmk({"encryption": {"type": "aes"}}))

    def test_analyse_s3_audit(self) -> None:
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
