from typing import Any, Dict, Set

from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings
from src.compliance.analyser import Analyser


class S3Compliance(Analyser):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._check_bucket_rules(report["account"], bucket)
            for report in audit.report
            for bucket in report["results"]["buckets"]
        }

    def _check_bucket_rules(self, account: Dict[str, str], bucket: Dict[str, Any]) -> Findings:
        findings = set()

        findings.update(self._check_encryption_bucket_rules(bucket))

        if not self._is_private(bucket):
            findings.add("bucket should not allow public access")

        if not self._is_tagged("expiry", bucket):
            findings.add("bucket should have data expiry tag")

        if not self._is_tagged("sensitivity", bucket):
            findings.add("bucket should have data sensitivity tag")

        if not self._has_logging(bucket):
            findings.add("bucket should have logging enabled")

        findings.update(self._check_high_sensitivity_bucket_rules(bucket))

        return Findings(
            account=Account.from_dict(account),
            compliance_item_type="s3_bucket",
            item=bucket["name"],
            findings=findings,
        )

    def _check_high_sensitivity_bucket_rules(self, bucket: Dict[str, Any]) -> Set[str]:
        findings = set()
        if bucket["data_tagging"]["sensitivity"] == "high":
            if not self._has_secure_transport(bucket):
                findings.add("bucket should have a resource policy with secure transport enforced")
            if not self._has_content_deny(bucket):
                findings.add("bucket should have a resource policy with a default deny action")
        return findings
    
    def _check_encryption_bucket_rules(self, bucket: Dict[str, Any]) -> Set[str]:
        findings = set()
        if self._is_encrypted(bucket):
            if not _is_rotation_enabled(bucket["kms_key"]):
                findings.add("kms key should have rotation enabled")
        else:
            findings.add("bucket should be encrypted")
        return findings

    def _is_enabled(self, key: str, bucket: Dict[str, Any]) -> bool:
        return bool(bucket.get(key, {}).get("enabled"))

    def _is_encrypted(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("encryption", bucket)
    
    def _is_rotation_enabled(self, kms_key: Dict[str, Any]) -> bool:
        return bool(kms_key.get(key, {}).get("rotation_enabled"))

    def _is_tagged(self, key: str, bucket: Dict[str, Any]) -> bool:
        return bool("unset" != bucket.get("data_tagging", {}).get(key, "unset"))

    def _is_private(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("public_access_block", bucket)

    def _has_secure_transport(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("secure_transport", bucket)

    def _has_content_deny(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("content_deny", bucket)

    def _has_logging(self, bucket: Dict[str, Any]) -> bool:
        return self._is_enabled("logging", bucket)
