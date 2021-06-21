from unittest import TestCase
from unittest.mock import Mock, patch
from src.report_fetcher import ReportFetcher
from src.config.config import Config


class TestReportFetcher(TestCase):
    def test_fetch_s3_report(self) -> None:
        s3_audit = {"some_key": "some_value"}
        s3_client = Mock(read_object=Mock(side_effect=lambda b, k: s3_audit if b == "bucket" and k == "key" else None))

        with patch.object(Config, "get_report_bucket", return_value="bucket"):
            with patch.object(Config, "get_s3_audit_report_key", return_value="key"):
                self.assertEqual(s3_audit, ReportFetcher(s3_client).fetch_s3_audit())
