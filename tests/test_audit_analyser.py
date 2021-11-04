from unittest import TestCase
from unittest.mock import Mock, patch

from src.audit_analyser import AuditAnalyser
from src.compliance.s3_compliance import S3Compliance
from src.compliance.github_compliance import GithubCompliance
from src.config.config import Config
from src.data.audit import Audit
from src.data.exceptions import UnsupportedAuditException

from tests.test_types_generator import findings


@patch.object(Config, "get_s3_audit_report_key", return_value="s3")
@patch.object(Config, "get_github_audit_report_key", return_value="github_admin_report")
class TestAuditAnalyser(TestCase):
    def test_check_s3_compliance(self, *_: Mock) -> None:
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="s3", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(S3Compliance, "analyse", return_value=notifications) as s3_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(audit, Config()))
        s3_compliance.assert_called_once_with(audit)

    def test_check_github_compliance(self, *_: Mock) -> None:
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="github_admin_report", report=[{"name": "some-repo"}, {"name": "some-repo-2"}])

        with patch.object(GithubCompliance, "analyse", return_value=notifications) as github_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(audit, Config()))
        github_compliance.assert_called_once_with(audit)

    def test_check_unsupported_audit(self, *_: Mock) -> None:
        with self.assertRaisesRegex(UnsupportedAuditException, "wat"):
            AuditAnalyser().analyse(Audit(type="wat", report=[]), Config())
