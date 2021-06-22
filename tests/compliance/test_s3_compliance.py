from unittest import TestCase

from src.data.audit import Audit
from src.compliance.s3_compliance import S3Compliance
from src.data.notification import Notification


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
        self.assertTrue(S3Compliance()._is_tagged(bucket))

    def test_bucket_has_one_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "unset", "sensitivity": "not_unset"}}
        self.assertFalse(S3Compliance()._is_tagged(bucket))

    def test_bucket_has_one_other_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "not_unset", "sensitivity": "unset"}}
        self.assertFalse(S3Compliance()._is_tagged(bucket))

    def test_bucket_has_one_missing_tag(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged({"data_tagging": {"sensitivity": "unset"}}))

    def test_bucket_has_other_missing_tag(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged({"data_tagging": {"expiry": "unset"}}))

    def test_bucket_has_tags_undefined(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged({"data_tagging": {}}))

    def test_bucket_tags_bucket_missing(self) -> None:
        self.assertFalse(S3Compliance()._is_tagged({}))

    def test_check(self) -> None:
        audit = Audit(
            type="s3",
            report=[
                {
                    "account": {
                        "identifier": "555666777444",
                    },
                    "results": {
                        "buckets": [
                            {
                                "name": "good-bucket",
                                "encryption": {"enabled": True},
                                "public_access_block": {"enabled": True},
                                "mfa_delete": {"enabled": False},
                                "data_tagging": {"expiry": "not_unset", "sensitivity": "not_unset"},
                            },
                            {
                                "name": "bad-bucket",
                                "encryption": {"enabled": False},
                                "mfa_delete": {"enabled": False},
                                "public_access_block": {"enabled": True},
                                "data_tagging": {"expiry": "unset", "sensitivity": "high"},
                            },
                        ]
                    },
                },
                {
                    "account": {
                        "identifier": "111222333444",
                    },
                    "results": {
                        "buckets": [
                            {
                                "name": "mischievous-bucket",
                                "encryption": {"enabled": True},
                                "mfa_delete": {"enabled": True},
                                "public_access_block": {"enabled": False},
                                "data_tagging": {"expiry": "unset", "sensitivity": "high"},
                            },
                        ]
                    },
                },
            ],
        )
        notifications = S3Compliance().check(audit)
        self.assertEqual(
            {
                Notification(
                    item="mischievous-bucket",
                    findings={
                        "bucket should not allow public access",
                        "bucket should have data expiry and data sensitivity tags",
                    },
                ),
                Notification(
                    item="bad-bucket",
                    findings={
                        "bucket should be encrypted",
                        "bucket should have mfa-delete",
                        "bucket should have data expiry and data sensitivity tags",
                    },
                ),
                Notification(item="good-bucket", findings=set()),
            },
            notifications,
        )
