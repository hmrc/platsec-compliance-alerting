from unittest.mock import Mock

from src.config.config import Config
from tests.fixtures.github_webhook_compliance import github_webhook_report
from tests.test_compliance_alerter import github_webhook_host_ignore_list
from tests.test_types_generator import findings

from src.data.audit import Audit
from src.compliance.github_webhook_compliance import GithubWebhookCompliance


def get_config() -> Mock:
    mock = Mock(spec=Config)
    mock.get_github_webhook_host_ignore_list.return_value = github_webhook_host_ignore_list
    return mock


def test_webhook_is_insecure_url() -> None:
    assert GithubWebhookCompliance(get_config())._is_insecure_url({"config": {"insecure_url": 1}})


def test_webhook_is_secure_url() -> None:
    assert not (GithubWebhookCompliance(get_config())._is_insecure_url({"config": {"insecure_url": 0}}))


def test_webhook_in_ignore_host_list() -> None:
    assert GithubWebhookCompliance(get_config())._in_ignore_host_list("https://known-host.com")


def test_webhook_not_in_ignore_host_list() -> None:
    assert not GithubWebhookCompliance(get_config())._in_ignore_host_list("https://unknown-host.com")


def test_webhook_with_port_in_ignore_list() -> None:
    assert GithubWebhookCompliance(get_config())._in_ignore_host_list("https://known-host.com:8443")


def test_webhook_with_port_and_path_in_ignore_host_list() -> None:
    assert GithubWebhookCompliance(get_config())._in_ignore_host_list("https://known-host.com:8443/something")


def test_check() -> None:
    audit = Audit(
        type="github_webhook_report1.json",
        report=github_webhook_report,
    )
    notifications = GithubWebhookCompliance(get_config()).analyse(audit)

    expected_findings = {
        findings(
            account=None,
            description="`https://known-host.com`",
            compliance_item_type="github_repository_webhook",
            item="https://known-host.com",
            findings={
                "webhook is set to insecure_url for `repository-with-insecure-url`",
            },
        ),
        findings(
            account=None,
            description="`https://unknown-host.com`",
            compliance_item_type="github_repository_webhook",
            item="https://unknown-host.com",
            findings={
                "webhook is unknown for `repository-with-2-unknown-urls`",
                "webhook is unknown for `repository-with-unknown-url`",
            },
        ),
    }
    assert notifications == expected_findings
