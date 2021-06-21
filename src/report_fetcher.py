from typing import Any, Dict

from src.config.config import Config
from src.clients.aws_s3_client import AwsS3Client


class ReportFetcher:
    def __init__(self, s3: AwsS3Client):
        self._config = Config()
        self._s3 = s3

    def fetch_s3_audit(self) -> Dict[str, Any]:
        return self._s3.read_object(self._config.get_report_bucket(), self._config.get_s3_audit_report_key())
