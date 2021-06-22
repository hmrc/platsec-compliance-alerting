from typing import Any, Dict, Set

from src.data.audit import Audit
from src.data.notification import Notification


class S3Compliance:
    def analyse(self, audit: Audit) -> Set[Notification]:
        return {self._check_bucket_rules(bucket) for report in audit.report for bucket in report["results"]["buckets"]}

    def _check_bucket_rules(self, bucket: Dict[str, Any]) -> Notification:
        findings = set()

        if not self._is_encrypted(bucket):
            findings.add("bucket should be encrypted")

        if not self._is_private(bucket):
            findings.add("bucket should not allow public access")

        if not self._is_tagged(bucket):
            findings.add("bucket should have data expiry and data sensitivity tags")

        findings.update(self._check_high_sensitivity_bucket_rules(bucket))

        return Notification(item=bucket["name"], findings=findings)

    def _check_high_sensitivity_bucket_rules(self, bucket: Dict[str, Any]) -> Set[str]:
        findings = set()
        if bucket["data_tagging"]["sensitivity"] == "high":
            if not self._is_mfa_delete(bucket):
                findings.add("bucket should have mfa-delete")
        return findings

    def _is_enabled(self, key: str, bucket: Dict[str, Any]) -> bool:
        return bool(bucket.get(key, {}).get("enabled"))

    def _is_encrypted(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("encryption", bucket)

    def _is_tagged(self, bucket: Dict[str, Any]) -> bool:
        return "unset" not in [
            bucket.get("data_tagging", {}).get("expiry", "unset"),
            bucket.get("data_tagging", {}).get("sensitivity", "unset"),
        ]

    def _is_private(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("public_access_block", bucket)

    def _is_mfa_delete(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("mfa_delete", bucket)
