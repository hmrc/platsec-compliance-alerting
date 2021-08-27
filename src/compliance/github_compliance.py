from typing import Any, Dict, Set

from src.data.audit import Audit
from src.data.account import Account
from src.data.notification import Notification
from src.compliance.analyser_interface import AnalyserInterface


class GithubCompliance(AnalyserInterface):
    def analyse(self, audit: Audit) -> Set[Notification]:
        return {self._check_repository_rules(repository) for repository in audit.report}

    def _check_repository_rules(self, repository: Dict[str, Any]) -> Notification:
        findings = set()

        if not self._is_signed(repository):
            findings.add("repository commit signing should be turned on")

        if not self._is_admin_permission(repository):
            findings.add("repository should have admin permissions")

        name = repository["name"]

        return Notification(Account.from_dict({"name": name, "identifier": name}), item=name, findings=findings)

    def _is_signed(self, repository: Dict[str, Any]) -> bool:
        for branchProtectionRule in repository["branchProtectionRules"]["nodes"]:
            if branchProtectionRule["requiresCommitSignatures"] is True:
                return True

        return False

    def _is_admin_permission(self, repository: Dict[str, Any]) -> bool:
        return bool(repository["teamPermissions"] == "ADMIN")
