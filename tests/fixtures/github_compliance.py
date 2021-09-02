github_report = [
    {
        "deleteBranchOnMerge": False,
        "isArchived": False,
        "isEmpty": False,
        "isFork": False,
        "isPrivate": True,
        "mergeCommitAllowed": True,
        "name": "good-repo",
        "nameWithOwner": "org/good-repo",
        "rebaseMergeAllowed": True,
        "squashMergeAllowed": True,
        "teamPermissions": "ADMIN",
        "branchProtectionRules": {
            "nodes": [
                {
                    "isAdminEnforced": False,
                    "requiresCommitSignatures": True,
                    "restrictsPushes": False,
                    "requiresApprovingReviews": False,
                    "requiresStatusChecks": False,
                    "requiresCodeOwnerReviews": False,
                    "dismissesStaleReviews": False,
                    "requiresStrictStatusChecks": True,
                    "requiredApprovingReviewCount": 0,
                    "allowsForcePushes": True,
                    "allowsDeletions": True,
                    "pattern": "main",
                }
            ]
        },
        "Parent": {"name": "", "nameWithOwner": "", "url": ""},
        "DefaultBranchRef": {"name": "main"},
    },
    {
        "deleteBranchOnMerge": False,
        "isArchived": False,
        "isEmpty": False,
        "isFork": False,
        "isPrivate": True,
        "mergeCommitAllowed": True,
        "name": "bad-repo-no-signing",
        "nameWithOwner": "org/bad-repo-no-signing",
        "rebaseMergeAllowed": True,
        "squashMergeAllowed": True,
        "teamPermissions": "ADMIN",
        "branchProtectionRules": {
            "nodes": [
                {
                    "isAdminEnforced": False,
                    "requiresCommitSignatures": False,
                    "restrictsPushes": False,
                    "requiresApprovingReviews": False,
                    "requiresStatusChecks": False,
                    "requiresCodeOwnerReviews": False,
                    "dismissesStaleReviews": False,
                    "requiresStrictStatusChecks": True,
                    "requiredApprovingReviewCount": 0,
                    "allowsForcePushes": True,
                    "allowsDeletions": True,
                    "pattern": "main",
                }
            ]
        },
        "Parent": {"name": "", "nameWithOwner": "", "url": ""},
        "DefaultBranchRef": {"name": "main"},
    },
    {
        "deleteBranchOnMerge": False,
        "isArchived": False,
        "isEmpty": False,
        "isFork": False,
        "isPrivate": True,
        "mergeCommitAllowed": True,
        "name": "bad-repo-no-admin",
        "nameWithOwner": "org/bad-repo-no-admin",
        "rebaseMergeAllowed": True,
        "squashMergeAllowed": True,
        "teamPermissions": "WRITE",
        "branchProtectionRules": {
            "nodes": [
                {
                    "isAdminEnforced": False,
                    "requiresCommitSignatures": True,
                    "restrictsPushes": False,
                    "requiresApprovingReviews": False,
                    "requiresStatusChecks": False,
                    "requiresCodeOwnerReviews": False,
                    "dismissesStaleReviews": False,
                    "requiresStrictStatusChecks": True,
                    "requiredApprovingReviewCount": 0,
                    "allowsForcePushes": True,
                    "allowsDeletions": True,
                    "pattern": "main",
                }
            ]
        },
        "Parent": {"name": "", "nameWithOwner": "", "url": ""},
        "DefaultBranchRef": {"name": "main"},
    },
    {
        "deleteBranchOnMerge": False,
        "isArchived": False,
        "isEmpty": False,
        "isFork": True,
        "isPrivate": True,
        "mergeCommitAllowed": True,
        "name": "bad-repo-no-admin",
        "nameWithOwner": "org/bad-repo-no-admin-forked",
        "rebaseMergeAllowed": True,
        "squashMergeAllowed": True,
        "teamPermissions": "WRITE",
        "branchProtectionRules": {
            "nodes": [
                {
                    "isAdminEnforced": False,
                    "requiresCommitSignatures": True,
                    "restrictsPushes": False,
                    "requiresApprovingReviews": False,
                    "requiresStatusChecks": False,
                    "requiresCodeOwnerReviews": False,
                    "dismissesStaleReviews": False,
                    "requiresStrictStatusChecks": True,
                    "requiredApprovingReviewCount": 0,
                    "allowsForcePushes": True,
                    "allowsDeletions": True,
                    "pattern": "main",
                }
            ]
        },
        "Parent": {"name": "", "nameWithOwner": "", "url": ""},
        "DefaultBranchRef": {"name": "main"},
    },
]
