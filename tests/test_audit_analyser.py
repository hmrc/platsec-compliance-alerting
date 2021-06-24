from unittest import TestCase
from unittest.mock import Mock, patch

from src.audit_analyser import AuditAnalyser
from src.compliance.s3_compliance import S3Compliance
from src.config.config import Config
from src.data.audit import Audit
from src.data.exceptions import UnsupportedAuditException
from src.data.notification import Notification


@patch.object(Config, "get_s3_audit_report_key", return_value="s3")
class TestAuditAnalyser(TestCase):
    def test_check_s3_compliance(self, _: Mock) -> None:
        notifications = {Notification("item-1", findings={"finding-1"}), Notification("item-2", findings={"finding-2"})}
        audit = Audit(type="s3", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(S3Compliance, "analyse", return_value=notifications) as s3_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(audit, Config()))
        s3_compliance.assert_called_once_with(audit)

    def test_check_unsupported_audit(self, _: Mock) -> None:
        with self.assertRaisesRegex(UnsupportedAuditException, "wat"):
            AuditAnalyser().analyse(Audit(type="wat", report=[]), Config())
