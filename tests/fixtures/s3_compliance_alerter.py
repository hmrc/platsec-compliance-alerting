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
                    "logging": {"enabled": True},
                    "kms_key": {"rotation_enabled": True},
                },
                {
                    "name": "bad-bucket",
                    "encryption": {"enabled": False},
                    "secure_transport": {},
                    "public_access_block": {"enabled": True},
                    "data_tagging": {"expiry": "1-week", "sensitivity": "unset"},
                    "kms_key": {"rotation_enabled": False},
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
                    "kms_key": {"rotation_enabled": True},
                },
            ]
        },
    },
]
