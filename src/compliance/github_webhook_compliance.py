from logging import Logger
from typing import Any, Dict, Set, List
from urllib.parse import urlparse

from src.compliance.analyser import Analyser
from src.config.config import Config
from src.data.audit import Audit
from src.data.finding import Finding


class GithubWebhookCompliance(Analyser):
    webhooks: Dict[str, Set[str]] = {}

    def __init__(self, logger: Logger, config: Config):
        self.config = config
        super().__init__(logger=logger, item_type="github_repository_webhook")

    def analyse(self, audit: Audit) -> Set[Finding]:
        for repositories in audit.report:
            for webhook in repositories["Webhooks"]:
                self._check_webhook_rules(repositories["RepositoryName"], webhook)

        return {self._set_all_findings(webhookURL, self.webhooks[webhookURL]) for webhookURL in self.webhooks}

    def _check_webhook_rules(self, repository: str, webhook: Dict[str, Any]) -> None:
        findings = set()

        webhookURL = webhook["config"]["url"]

        if self._is_insecure_url(webhook):
            self.logger.info(f"webhook '{webhookURL}' is set to insecure_url for '{repository}'")
            findings.add(f"webhook is set to insecure_url for `{repository}`")

        if not self._in_ignore_host_list(webhookURL):
            self.logger.info(f"webhook '{webhookURL}' is unknown for '{repository}'")
            findings.add(f"webhook is unknown for `{repository}`")

        if len(findings) > 0:
            if webhookURL in self.webhooks:
                self.webhooks[webhookURL].update(findings)
            else:
                self.webhooks[webhookURL] = findings

    def _set_all_findings(self, webhook: str, findings: Set[str]) -> Finding:
        return Finding(
            description=f"`{webhook}`",
            compliance_item_type=self.item_type,
            item=webhook,
            findings=findings,
        )

    def _is_insecure_url(self, webhook: Dict[str, Any]) -> bool:
        return bool(webhook["config"]["insecure_url"])

    def _in_ignore_host_list(self, url: str) -> bool:
        urlParse = urlparse(url)
        host = urlParse.hostname

        return bool(host in self._get_ignore_list())

    def _get_ignore_list(self) -> List[str]:
        return self.config.get_github_webhook_host_ignore_list()
