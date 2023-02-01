from typing import Any, Dict, Set

from src.data.audit import Audit
from src.data.findings import Findings
from src.compliance.analyser import Analyser


class GithubCompliance(Analyser):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return {self._check_repository_rules(repository) for repository in audit.report if not repository["isFork"]}

    def _check_repository_rules(self, repository: Dict[str, Any]) -> Findings:
        findings = set()

        if not self._is_signed(repository):
            findings.add("repository commit signing should be turned on")

        if not self._is_admin_permission(repository):
            findings.add("repository should have admin permissions")

        if self._has_wiki_enabled(repository):
            findings.add("repository has wiki enabled")

        return Findings(
            description=f"<https://www.github.com/{repository['nameWithOwner']}|{repository['name']}>",
            compliance_item_type="github_repository",
            item=repository["name"],
            findings=findings,
        )

    def _is_signed(self, repository: Dict[str, Any]) -> bool:
        return True in [bpr["requiresCommitSignatures"] for bpr in repository["branchProtectionRules"]["nodes"]]

    def _is_admin_permission(self, repository: Dict[str, Any]) -> bool:
        return bool(repository["teamPermissions"] == "ADMIN")

    def _has_wiki_enabled(self, repository: Dict[str, Any]) -> bool:
        return repository["hasWikiEnabled"] == True
