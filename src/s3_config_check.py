from typing import Any, Dict

from src.notification import Notification


class S3ConfigCheck:
    def check_bucket_rules(self, bucket: Dict[str, Any]) -> Notification:
        findings = set()

        if not self.is_encrypted(bucket):
            findings.add("bucket should be encrypted")

        if not self.is_private(bucket):
            findings.add("bucket should not allow public access")

        if not self.is_mfa_delete(bucket):
            findings.add("bucket should have mfa-delete")

        if not self.is_tagged(bucket):
            findings.add("bucket should have data expiry and data sensitivity tags")

        return Notification(bucket=bucket["name"], findings=findings)

    def _is_enabled(self, key: str, bucket: Dict[str, Any]) -> bool:
        return bool(bucket.get(key, {}).get("enabled"))

    def is_encrypted(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("encryption", bucket)

    def is_tagged(self, bucket: Dict[str, Any]) -> bool:
        return "unset" not in [
            bucket.get("data_tagging", {}).get("expiry", "unset"),
            bucket.get("data_tagging", {}).get("sensitivity", "unset"),
        ]

    def is_private(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("public_access_block", bucket)

    def is_mfa_delete(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("mfa_delete", bucket)
