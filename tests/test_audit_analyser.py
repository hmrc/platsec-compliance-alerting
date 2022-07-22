from logging import getLogger
from unittest import TestCase
from unittest.mock import Mock, patch

from src.audit_analyser import AuditAnalyser
from src.compliance.ec2_compliance import Ec2Compliance
from src.compliance.iam_compliance import IamCompliance
from src.compliance.s3_compliance import S3Compliance
from src.compliance.github_compliance import GithubCompliance
from src.compliance.github_webhook_compliance import GithubWebhookCompliance
from src.compliance.vpc_compliance import VpcCompliance
from src.compliance.vpc_peering_compliance import VpcPeeringCompliance
from src.compliance.password_policy_compliance import PasswordPolicyCompliance
from src.config.config import Config
from src.data.audit import Audit
from src.data.exceptions import UnsupportedAuditException

from tests.test_types_generator import findings


@patch.object(Config, "get_s3_audit_report_key", return_value="s3")
@patch.object(Config, "get_github_audit_report_key", return_value="github_admin_report")
@patch.object(Config, "get_github_webhook_report_key", return_value="github_webhook_report")
@patch.object(Config, "get_iam_audit_report_key", return_value="audit_iam.json")
@patch.object(Config, "get_vpc_audit_report_key", return_value="audit_vpc_flow_logs.json")
@patch.object(Config, "get_password_policy_audit_report_key", return_value="audit_password_policy.json")
@patch.object(Config, "get_vpc_peering_audit_report_key", return_value="audit_vpc_peering.json")
@patch.object(Config, "get_ec2_audit_report_key", return_value="audit_ec2.json")
class TestAuditAnalyser(TestCase):
    def test_check_s3_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="s3", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(S3Compliance, "analyse", return_value=notifications) as s3_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(logger, audit, Config()))
        s3_compliance.assert_called_once_with(logger, audit)

    def test_check_iam_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="audit_iam.json", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(IamCompliance, "analyse", return_value=notifications) as compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(logger, audit, Config()))
        compliance.assert_called_once_with(logger, audit)

    def test_check_github_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="github_admin_report", report=[{"name": "some-repo"}, {"name": "some-repo-2"}])

        with patch.object(GithubCompliance, "analyse", return_value=notifications) as github_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(logger, audit, Config()))
        github_compliance.assert_called_once_with(logger, audit)

    def test_check_github_webhook_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(
            type="github_webhook_report1",
            report=[
                {
                    "repository-with-unknown-url": [{"config": {"url": "https://unknown-host.com", "insecure_url": 0}}],
                    "repository-with-insecure-url": [
                        {"config": {"url": "https://insecure-host.com", "insecure_url": 1}}
                    ],
                }
            ],
        )

        with patch.object(GithubWebhookCompliance, "analyse", return_value=notifications) as github_webhook_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(logger, audit, Config()))
        github_webhook_compliance.assert_called_once_with(logger, audit)

    def test_check_vpc_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="audit_vpc_flow_logs.json", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(VpcCompliance, "analyse", return_value=notifications) as vpc_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(getLogger(), audit, Config()))
        vpc_compliance.assert_called_once_with(logger, audit)

    def test_check_vpc_peering_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        notifications = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="audit_vpc_peering.json", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(VpcPeeringCompliance, "analyse", return_value=notifications) as vpc_peering_compliance:
            self.assertEqual(notifications, AuditAnalyser().analyse(logger, audit, Config()))
        vpc_peering_compliance.assert_called_once_with(logger, audit)

    def test_check_password_policy_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        the_findings = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="audit_password_policy.json", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(PasswordPolicyCompliance, "analyse", return_value=the_findings) as password_policy_compliance:
            self.assertEqual(the_findings, AuditAnalyser().analyse(logger, audit, Config()))
        password_policy_compliance.assert_called_once_with(logger, audit)

    def test_ec2_policy_compliance(self, *_: Mock) -> None:
        logger = getLogger()
        the_findings = {findings(item="item-1"), findings(item="item-2")}
        audit = Audit(type="audit_ec2.json", report=[{"report": "val-1"}, {"report": "val-2"}])

        with patch.object(Ec2Compliance, "analyse", return_value=the_findings) as password_policy_compliance:
            self.assertEqual(the_findings, AuditAnalyser().analyse(getLogger(), audit, Config()))
        password_policy_compliance.assert_called_once_with(logger, audit)

    def test_check_unsupported_audit(self, *_: Mock) -> None:
        with self.assertRaisesRegex(UnsupportedAuditException, "wat"):
            AuditAnalyser().analyse(getLogger(), Audit(type="wat", report=[]), Config())
