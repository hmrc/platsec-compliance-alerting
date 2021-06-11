from typing import Any, Dict, List


class S3ConfigCheck:
    def check_bucket_compliance(self, bucket: Dict[str, Any]) -> List[str]:
        pass

    def is_encrypted(self, bucket: Dict[str, Any]) -> bool:
        return bucket.get("encryption", {}).get("enabled")

    def is_tagged(self, bucket: Dict[str, Any]) -> bool:
        return "unset" not in [
            bucket.get("data_tagging", {}).get("expiry", "unset"),
            bucket.get("data_tagging", {}).get("sensitivity", "unset"),
        ]

    def is_private(self, bucket: Dict[str, Any]) -> bool:
        return bucket.get("public_access_block", {}).get("enabled")