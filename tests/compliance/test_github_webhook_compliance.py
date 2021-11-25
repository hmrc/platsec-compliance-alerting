from unittest import TestCase

from tests.fixtures.github_webhook_compliance import github_webhook_report
from tests.test_types_generator import account, findings

from src.data.audit import Audit
from src.compliance.github_webhook_compliance import GithubWebhookCompliance


class TestGithubWebhookCompliance(TestCase):
    def test_repository_is_insecure_url(self) -> None:
        self.assertTrue(GithubWebhookCompliance()._is_insecure_url({"config": {"insecure_url": 1}}))

    def test_repository_is_secure_url(self) -> None:
        self.assertFalse(GithubWebhookCompliance()._is_insecure_url({"config": {"insecure_url": 0}}))

    def test_repository_in_ignore_host_list(self) -> None:
        self.assertTrue(GithubWebhookCompliance()._in_ignore_host_list("http://jira.tools.tax.service.gov.uk"))

    def test_repository_not_in_ignore_host_list(self) -> None:
        self.assertFalse(GithubWebhookCompliance()._in_ignore_host_list("http://some-webhook-url.com"))

    def test_check(self) -> None:
        audit = Audit(
            type="github_webhook_report1.json",
            report=github_webhook_report,
        )
        notifications = GithubWebhookCompliance().analyse(audit)
        self.assertEqual(
            {
                findings(
                    account=account("Github webhook", "http://hooks.slack.com"),
                    compliance_item_type="github_repository_webhook",
                    item="http://hooks.slack.com",
                    findings={
                        "webhook is set to insecure_url for repository-with-insecure-url",
                    },
                ),
                findings(
                    account=account("Github webhook", "https://unknown-host.com"),
                    compliance_item_type="github_repository_webhook",
                    item="https://unknown-host.com",
                    findings={
                        "webhook is unknown for repository-with-2-unknown-urls",
                    },
                ),
            },
            notifications,
        )
