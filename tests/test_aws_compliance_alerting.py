from unittest import TestCase

from src.aws_compliance_alerting import AwsComplianceAlertingMain


class TestAwsScannerMain(TestCase):
    def test_main(self):
        AwsComplianceAlertingMain()
