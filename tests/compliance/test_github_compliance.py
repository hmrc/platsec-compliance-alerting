from unittest import TestCase

from tests.fixtures.github_compliance import github_report
from tests.test_types_generator import findings

from src.data.audit import Audit
from src.compliance.github_compliance import GithubCompliance


class TestGithubCompliance(TestCase):
    def test_repository_is_signed(self) -> None:
        self.assertTrue(
            GithubCompliance()._is_signed({"branchProtectionRules": {"nodes": [{"requiresCommitSignatures": True}]}})
        )

    def test_repository_is_not_signed(self) -> None:
        self.assertFalse(
            GithubCompliance()._is_signed({"branchProtectionRules": {"nodes": [{"requiresCommitSignatures": False}]}})
        )

    def test_repository_is_signed_with_multiple_nodes(self) -> None:
        self.assertTrue(
            GithubCompliance()._is_signed(
                {
                    "branchProtectionRules": {
                        "nodes": [
                            {"requiresCommitSignatures": False},
                            {"requiresCommitSignatures": True},
                        ]
                    }
                }
            )
        )

    def test_repository_is_signed_with_multiple_nodes_false(self) -> None:
        self.assertFalse(
            GithubCompliance()._is_signed(
                {
                    "branchProtectionRules": {
                        "nodes": [
                            {"requiresCommitSignatures": False},
                            {"requiresCommitSignatures": False},
                        ]
                    }
                }
            )
        )

    def test_repository_is_admin_permission(self) -> None:
        self.assertTrue(GithubCompliance()._is_admin_permission({"teamPermissions": "ADMIN"}))

    def test_repository_is_not_admin_permission(self) -> None:
        self.assertFalse(GithubCompliance()._is_admin_permission({"teamPermissions": "WRITE"}))

    def test_check(self) -> None:
        audit = Audit(
            type="github_admin_report.json",
            report=github_report,
        )
        notifications = GithubCompliance().analyse(audit)
        expected_findings = {
            findings(
                account=None,
                description="<https://www.github.com/org/bad-repo-no-signing|bad-repo-no-signing>",
                compliance_item_type="github_repository",
                item="bad-repo-no-signing",
                findings={
                    "repository commit signing should be turned on",
                },
            ),
            findings(
                account=None,
                description="<https://www.github.com/org/bad-repo-no-admin|bad-repo-no-admin>",
                compliance_item_type="github_repository",
                item="bad-repo-no-admin",
                findings={
                    "repository should have admin permissions",
                },
            ),
            findings(
                account=None,
                description="<https://www.github.com/org/good-repo|good-repo>",
                compliance_item_type="github_repository",
                item="good-repo",
                findings=set(),
            ),
        }
        assert notifications == expected_findings
