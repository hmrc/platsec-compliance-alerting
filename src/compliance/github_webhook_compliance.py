from typing import Any, Dict, Set
from urllib.parse import urlparse

from src.compliance.analyser import Analyser
from src.data.audit import Audit
from src.data.account import Account
from src.data.findings import Findings


class GithubWebhookCompliance(Analyser):
    webhooks: Dict[str, Set[str]] = {}

    def analyse(self, audit: Audit) -> Set[Findings]:
        for repositories in audit.report:
            for webhook in repositories["Webhooks"]:
                self._check_webhook_rules(repositories["RepositoryName"], webhook)

        return {self._set_all_findings(webhookURL, self.webhooks[webhookURL]) for webhookURL in self.webhooks}

    def _check_webhook_rules(self, repository: str, webhook: Dict[str, Any]) -> None:
        findings = set()

        webhookURL = webhook["config"]["url"]

        if self._is_insecure_url(webhook):
            findings.add(f"webhook is set to insecure_url for {repository}")

        if not self._in_ignore_host_list(webhookURL):
            findings.add(f"webhook is unknown for {repository}")

        if len(findings) > 0:
            self.webhooks[webhookURL] = findings

    def _set_all_findings(self, webhook: str, findings: Set[str]) -> Findings:
        return Findings(
            Account("Github webhook", webhook),
            compliance_item_type="github_repository_webhook",
            item=webhook,
            findings=findings,
        )

    def _is_insecure_url(self, webhook: Dict[str, Any]) -> bool:
        return bool(webhook["config"]["insecure_url"])

    def _in_ignore_host_list(self, url: str) -> bool:
        urlParse = urlparse(url)
        host = urlParse.netloc

        """Pass this list in from a config file"""
        ignoreList = [
            "jira.tools.tax.service.gov.uk",
            "hooks.slack.com",
            "jira-staging.tools.tax.service.gov.uk",
            "jenkins.tools.management.tax.service.gov.uk",
            "codebuild.eu-west-2.amazonaws.com",
        ]
        return bool(host in ignoreList)
