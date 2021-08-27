from typing import Any, Dict, Set

from src.data.audit import Audit
from src.data.account import Account
from src.data.notification import Notification
from src.compliance.analyser_interface import AnalyserInterface


class S3Compliance(AnalyserInterface):
    def analyse(self, audit: Audit) -> Set[Notification]:
        return {
            self._check_bucket_rules(report["account"], bucket)
            for report in audit.report
            for bucket in report["results"]["buckets"]
        }

    def _check_bucket_rules(self, account: Dict[str, str], bucket: Dict[str, Any]) -> Notification:
        findings = set()

        if not self._is_encrypted(bucket):
            findings.add("bucket should be encrypted")

        if not self._is_private(bucket):
            findings.add("bucket should not allow public access")

        if not self._is_tagged("expiry", bucket):
            findings.add("bucket should have data expiry tag")

        if not self._is_tagged("sensitivity", bucket):
            findings.add("bucket should have data sensitivity tag")

        findings.update(self._check_high_sensitivity_bucket_rules(bucket))

        return Notification(account=Account.from_dict(account), item=bucket["name"], findings=findings)

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

    def _is_tagged(self, key: str, bucket: Dict[str, Any]) -> bool:
        return bool("unset" != bucket.get("data_tagging", {}).get(key, "unset"))

    def _is_private(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("public_access_block", bucket)

    def _is_mfa_delete(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("mfa_delete", bucket)
