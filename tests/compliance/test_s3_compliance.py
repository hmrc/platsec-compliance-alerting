from unittest import TestCase

from tests.fixtures.s3_compliance import s3_report
from tests.test_types_generator import account, findings

from src.data.audit import Audit
from src.compliance.s3_compliance import S3Compliance


class TestS3Compliance(TestCase):
    def test_key_is_enabled(self) -> None:
        self.assertTrue(S3Compliance()._is_enabled("encryption", {"encryption": {"enabled": True}}))

    def test_key_is_disabled(self) -> None:
        self.assertFalse(S3Compliance()._is_enabled("encryption", {"encryption": {"enabled": False}}))

    def test_key_bucket_missing(self) -> None:
        self.assertFalse(S3Compliance()._is_enabled("encryption", {}))

    def test_key_undefined(self) -> None:
        self.assertFalse(S3Compliance()._is_enabled("encryption", {"encryption": {}}))

    def test_bucket_has_tags(self) -> None:
        bucket = {"data_tagging": {"expiry": "not_unset", "sensitivity": "not_unset"}}
        self.assertTrue(S3Compliance()._is_tagged("expiry", bucket))

    def test_bucket_has_one_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "unset", "sensitivity": "not_unset"}}
        self.assertFalse(S3Compliance()._is_tagged("expiry", bucket))

    def test_bucket_has_one_other_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "not_unset", "sensitivity": "unset"}}
        self.assertFalse(S3Compliance()._is_tagged("sensitivity", bucket))

    def test_bucket_has_one_missing_tag(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged("expiry", {"data_tagging": {"sensitivity": "unset"}}))

    def test_bucket_has_other_missing_tag(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged("sensitivity", {"data_tagging": {"expiry": "unset"}}))

    def test_bucket_has_expiry_tag_undefined(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged("expiry", {"data_tagging": {}}))

    def test_bucket_expiry_tag_bucket_missing(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged("expiry", {}))

    def test_bucket_has_sensitivity_tag_undefined(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged("sensitivity", {"data_tagging": {}}))

    def test_bucket_sensitivity_tag_bucket_missing(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged("sensitivity", {}))

    def test_check(self) -> None:
        audit = Audit(
            type="s3",
            report=s3_report,
        )
        notifications = S3Compliance().analyse(audit)
        self.assertEqual(
            {
                findings(
                    account=account("111222333444", "another-account"),
                    item="mischievous-bucket",
                    findings={
                        "bucket should have mfa-delete",
                        "bucket should not allow public access",
                        "bucket should have data expiry tag",
                    },
                ),
                findings(
                    account=account("555666777444", "an-account"),
                    item="bad-bucket",
                    findings={
                        "bucket should be encrypted",
                        "bucket should have data sensitivity tag",
                    },
                ),
                findings(account=account("555666777444", "an-account"), item="good-bucket", findings=set()),
                findings(
                    account=account("999999999999", "another-account-2"),
                    item="good-bucket-high-sensitivity",
                    findings=set(),
                ),
            },
            notifications,
        )
