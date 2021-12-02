from typing import List, Dict, Any

github_webhook_report: List[Dict[str, Any]] = [
    {
        "RepositoryName": "repository-with-insecure-url",
        "Webhooks": [
            {
                "config": {"url": "https://hooks.slack.com", "insecure_url": 0},
                "active": True,
                "id": 123,
                "events": ["push"],
            },
            {
                "config": {"url": "http://hooks.slack.com", "insecure_url": 1},
                "active": True,
                "id": 124,
                "events": ["issue_comment", "pull_request", "pull_request_review_comment", "push"],
            },
        ],
    },
    {
        "RepositoryName": "repository-with-2-unknown-urls",
        "Webhooks": [
            {
                "config": {"url": "https://unknown-host.com", "insecure_url": 0},
                "active": True,
                "id": 234,
                "events": ["push"],
            },
            {
                "config": {"url": "https://unknown-host.com", "insecure_url": 0},
                "active": True,
                "id": 235,
                "events": ["issue_comment", "pull_request", "pull_request_review_comment", "push"],
            },
        ],
    },
    {
        "RepositoryName": "repository-with-known-secure-hosts",
        "Webhooks": [
            {
                "config": {"url": "http://hooks.slack.com", "insecure_url": 0},
                "active": True,
                "id": 345,
                "events": ["push"],
            },
            {
                "config": {"url": "http://hooks.slack.com/", "insecure_url": 0},
                "active": True,
                "id": 346,
                "events": ["issue_comment", "pull_request", "pull_request_review_comment", "push"],
            },
        ],
    },
    {
        "RepositoryName": "repository-name-4",
        "Webhooks": [],
    },
]
