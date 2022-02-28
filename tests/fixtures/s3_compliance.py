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
                    "secure_transport": {},
                    "data_tagging": {"expiry": "not_unset", "sensitivity": "not_unset"},
                },
                {
                    "name": "bad-bucket",
                    "encryption": {"enabled": False},
                    "secure_transport": {},
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
                    "secure_transport": {},
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
                    "secure_transport": {"enabled": True},
                    "public_access_block": {"enabled": True},
                    "data_tagging": {"expiry": "1-week", "sensitivity": "high"},
                    "content_deny": {"enabled": True},
                },
            ]
        },
    },
    {
        "account": {
            "identifier": "999999999888",
            "name": "another-account-888",
        },
        "results": {
            "buckets": [
                {
                    "name": "bad-bucket-low-sensitivity",
                    "encryption": {"enabled": False},
                    "secure_transport": {},
                    "public_access_block": {"enabled": False},
                    "data_tagging": {"expiry": "unset", "sensitivity": "low"},
                },
            ]
        },
    },
]
