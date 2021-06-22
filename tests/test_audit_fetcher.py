from unittest import TestCase
from unittest.mock import Mock

from src.audit_fetcher import AuditFetcher
from src.data.exceptions import UnsupportedEventException
from src.data.audit import Audit


class TestReportFetcher(TestCase):
    def test_fetch_audit(self) -> None:
        report = [{"some_key": "some value"}]
        s3 = Mock(read_object=Mock(side_effect=lambda b, k: report if b == "buck" and k == "report" else None))
        event = {"Records": [{"eventVersion": "2.1", "s3": {"bucket": {"name": "buck"}, "object": {"key": "report"}}}]}
        self.assertEqual(Audit(type="report", report=report), AuditFetcher().fetch_audit(s3, event))

    def test_fetch_audit_unsupported_event(self) -> None:
        with self.assertRaisesRegex(UnsupportedEventException, "expected event version >=2 and <3"):
            AuditFetcher().fetch_audit(Mock(), {})

        with self.assertRaisesRegex(UnsupportedEventException, "'eventVersion': '1.9'"):
            AuditFetcher().fetch_audit(Mock(), {"Records": [{"eventVersion": "1.9"}]})

        with self.assertRaisesRegex(UnsupportedEventException, "'eventVersion': '3.0'"):
            AuditFetcher().fetch_audit(Mock(), {"Records": [{"eventVersion": "3.0"}]})
