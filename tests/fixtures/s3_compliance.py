s3_report = [
    {
        "account": {
            "identifier": "555666777444",
            "name": "an-account",
        },
        "results": {
            "buckets": [
                {
                    "name": "good-bucket",
                    "encryption": {"enabled": True},
                    "public_access_block": {"enabled": True},
                    "mfa_delete": {"enabled": False},
                    "data_tagging": {"expiry": "not_unset", "sensitivity": "not_unset"},
                },
                {
                    "name": "bad-bucket",
                    "encryption": {"enabled": False},
                    "mfa_delete": {"enabled": False},
                    "public_access_block": {"enabled": True},
                    "data_tagging": {"expiry": "1-week", "sensitivity": "unset"},
                },
            ]
        },
    },
    {
        "account": {
            "identifier": "111222333444",
            "name": "another-account",
        },
        "results": {
            "buckets": [
                {
                    "name": "mischievous-bucket",
                    "encryption": {"enabled": True},
                    "mfa_delete": {"enabled": False},
                    "public_access_block": {"enabled": False},
                    "data_tagging": {"expiry": "unset", "sensitivity": "high"},
                },
            ]
        },
    },
    {
        "account": {
            "identifier": "999999999999",
            "name": "another-account-2",
        },
        "results": {
            "buckets": [
                {
                    "name": "good-bucket-high-sensitivity",
                    "encryption": {"enabled": True},
                    "mfa_delete": {"enabled": True},
                    "public_access_block": {"enabled": True},
                    "data_tagging": {"expiry": "1-week", "sensitivity": "high"},
                },
            ]
        },
    },
]
