from unittest import TestCase

from src.s3_config_check import S3ConfigCheck


class TestS3ConfigCheck(TestCase):
    def test_bucket_is_encrypted(self) -> None:
        bucket = {"encryption": {"enabled": True}}
        self.assertTrue(S3ConfigCheck().is_encrypted(bucket))

    def test_bucket_is_not_encrypted(self) -> None:
        bucket = {"encryption": {"enabled": False}}
        self.assertFalse(S3ConfigCheck().is_encrypted(bucket))

    def test_bucket_encryption_bucket_missing(self) -> None:
        self.assertFalse(S3ConfigCheck().is_encrypted({}))

    def test_bucket_encryption_undefined(self) -> None:
        self.assertFalse(S3ConfigCheck().is_encrypted({"encryption": {}}))

    def test_bucket_has_tags(self) -> None:
        bucket = {"data_tagging": {"expiry": "not_unset", "sensitivity": "not_unset"}}
        self.assertTrue(S3ConfigCheck().is_tagged(bucket))

    def test_bucket_has_one_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "unset", "sensitivity": "not_unset"}}
        self.assertFalse(S3ConfigCheck().is_tagged(bucket))

    def test_bucket_has_one_other_bad_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "not_unset", "sensitivity": "unset"}}
        self.assertFalse(S3ConfigCheck().is_tagged(bucket))

    def test_bucket_has_one_missing_tag(self) -> None:
        bucket = {"data_tagging": {"sensitivity": "unset"}}
        self.assertFalse(S3ConfigCheck().is_tagged(bucket))

    def test_bucket_has_other_missing_tag(self) -> None:
        bucket = {"data_tagging": {"expiry": "unset"}}
        self.assertFalse(S3ConfigCheck().is_tagged(bucket))

    def test_bucket_has_tags_undefined(self) -> None:
        self.assertFalse(S3ConfigCheck().is_tagged({"data_tagging": {}}))

    def test_bucket_tags_bucket_missing(self) -> None:
        self.assertFalse(S3ConfigCheck().is_tagged({}))

    def test_bucket_is_private(self) -> None:
        bucket = {"public_access_block": {"enabled": True}}
        self.assertTrue(S3ConfigCheck().is_private(bucket))

    def test_bucket_is_private_bucket_missing(self) -> None:
        self.assertFalse(S3ConfigCheck().is_private({}))

    def test_bucket_is_not_private(self) -> None:
        bucket = {"public_access_block": {"enabled": False}}
        self.assertFalse(S3ConfigCheck().is_private(bucket))

    def test_bucket_is_private_undefined(self) -> None:
        self.assertFalse(S3ConfigCheck().is_private({"public_access_block": {}}))
