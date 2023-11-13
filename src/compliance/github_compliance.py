from typing import Any, Dict, Set
from logging import Logger

from src.data.audit import Audit
from src.data.finding import Finding
from src.compliance.analyser import Analyser


class GithubCompliance(Analyser):
    def __init__(self, logger: Logger, enable_wiki_checking: bool) -> None:
        super().__init__(logger=logger, item_type="github_repository")
        self.enable_wiki_checking = enable_wiki_checking

    def analyse(self, audit: Audit) -> Set[Finding]:
        return {self._check_repository_rules(repository) for repository in audit.report if not repository["isFork"]}

    def _check_repository_rules(self, repository: Dict[str, Any]) -> Finding:
        findings = set()

        if not self._is_signed(repository):
            findings.add("repository commit signing should be turned on")

        if not self._is_admin_permission(repository):
            findings.add("repository should have admin permissions")

        if self._has_wiki_enabled(repository):
            findings.add("repository has wiki enabled")

        return Finding(
            description=f"<https://www.github.com/{repository['nameWithOwner']}|{repository['name']}>",
            compliance_item_type=self.item_type,
            item=repository["name"],
            findings=findings,
        )

    def _is_signed(self, repository: Dict[str, Any]) -> bool:
        return True in [bpr["requiresCommitSignatures"] for bpr in repository["branchProtectionRules"]["nodes"]]

    def _is_admin_permission(self, repository: Dict[str, Any]) -> bool:
        return bool(repository["teamPermissions"] == "ADMIN")

    def _has_wiki_enabled(self, repository: Dict[str, Any]) -> bool:
        if self.enable_wiki_checking:
            return repository["hasWikiEnabled"] is True
        else:
            return False
