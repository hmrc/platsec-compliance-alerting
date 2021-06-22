from typing import Any, Dict, Tuple

from src.clients.aws_s3_client import AwsS3Client
from src.data.audit import Audit
from src.data.exceptions import UnsupportedEventException


class AuditFetcher:
    def fetch_audit(self, s3: AwsS3Client, event: Dict[str, Any]) -> Audit:
        bucket, key = self._read_event(event)
        return Audit(type=key, report=s3.read_object(bucket, key))

    @staticmethod
    def _read_event(event: Dict[str, Any]) -> Tuple[str, str]:
        if not event.get("Records", [{}])[0].get("eventVersion", "").startswith("2."):
            raise UnsupportedEventException(f"expected event version >=2 and <3, got {event}")
        return event["Records"][0]["s3"]["bucket"]["name"], event["Records"][0]["s3"]["object"]["key"]
