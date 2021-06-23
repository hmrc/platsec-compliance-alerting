s3_report = [
    {
        "account": {
            "identifier": "555666777444",
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
                    "data_tagging": {"expiry": "unset", "sensitivity": "high"},
                },
            ]
        },
    },
    {
        "account": {
            "identifier": "111222333444",
        },
        "results": {
            "buckets": [
                {
                    "name": "mischievous-bucket",
                    "encryption": {"enabled": True},
                    "mfa_delete": {"enabled": True},
                    "public_access_block": {"enabled": False},
                    "data_tagging": {"expiry": "unset", "sensitivity": "high"},
                },
            ]
        },
    },
]
