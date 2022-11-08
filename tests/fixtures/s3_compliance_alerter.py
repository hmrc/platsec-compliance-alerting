s3_report = [
    {
        "account": {
            "identifier": "555666777444",
            "name": "an-account",
        },
        "region": "test-region-name",
        "results": {
            "buckets": [
                {
                    "name": "good-bucket",
                    "compliancy": {
                        "content_deny": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "acl": {"compliant": True, "message": "bucket should not have ACL set"},
                        "encryption": {"compliant": True, "message": "bucket should be encrypted"},
                        "logging": {"compliant": True, "message": "bucket should have logging enabled"},
                        "public_access_block": {"compliant": True, "message": "bucket should not allow public access"},
                        "secure_transport": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with secure transport enforced",
                        },
                        "versioning": {"compliant": True, "message": "bucket should have versioning enabled"},
                        "mfa_delete": {"compliant": True, "message": "MFA delete should be disabled"},
                        "kms_key": {"compliant": True, "message": "bucket kms key should have rotation enabled"},
                        "tagging": {"compliant": True, "message": "bucket should tags for expiry and sensitivity"},
                        "lifecycle": {"compliant": True, "message": "bucket should have a lifecycle configuration set"},
                        "cors": {"compliant": True, "message": "bucket should not have CORS set"},
                    },
                    "encryption": {"enabled": True},
                    "public_access_block": {"enabled": True},
                    "secure_transport": {},
                    "data_tagging": {"expiry": "not_unset", "sensitivity": "not_unset"},
                    "logging": {"enabled": True},
                    "kms_key": {"rotation_enabled": True},
                },
                {
                    "name": "bad-bucket",
                    "compliancy": {
                        "content_deny": {
                            "compliant": False,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "acl": {"compliant": False, "message": "bucket should not have ACL set"},
                        "encryption": {"compliant": False, "message": "bucket should be encrypted"},
                        "logging": {"compliant": False, "message": "bucket should have logging enabled"},
                        "public_access_block": {"compliant": False, "message": "bucket should not allow public access"},
                        "secure_transport": {
                            "compliant": False,
                            "message": "bucket should have a resource policy with secure transport enforced",
                        },
                        "versioning": {"compliant": False, "message": "bucket should have versioning enabled"},
                        "mfa_delete": {"compliant": False, "message": "MFA delete should be disabled"},
                        "kms_key": {"compliant": False, "message": "bucket kms key should have rotation enabled"},
                        "tagging": {"compliant": False, "message": "bucket should tags for expiry and sensitivity"},
                        "lifecycle": {
                            "compliant": False,
                            "message": "bucket should have a lifecycle configuration set",
                        },
                        "cors": {"compliant": False, "message": "bucket should not have CORS set"},
                    },
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
        "region": "test-region-name",
        "results": {
            "buckets": [
                {
                    "name": "mischievous-bucket",
                    "compliancy": {
                        "content_deny": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "acl": {"compliant": True, "message": "bucket should not have ACL set"},
                        "encryption": {"compliant": True, "message": "bucket should be encrypted"},
                        "logging": {"compliant": True, "message": "bucket should have logging enabled"},
                        "public_access_block": {"compliant": False, "message": "bucket should not allow public access"},
                        "secure_transport": {
                            "compliant": False,
                            "message": "bucket should have a resource policy with secure transport enforced",
                        },
                        "versioning": {"compliant": True, "message": "bucket should have versioning enabled"},
                        "mfa_delete": {"compliant": True, "message": "MFA delete should be disabled"},
                        "kms_key": {"compliant": False, "message": "bucket kms key should have rotation enabled"},
                        "tagging": {"compliant": False, "message": "bucket should tags for expiry and sensitivity"},
                        "lifecycle": {"compliant": True, "message": "bucket should have a lifecycle configuration set"},
                        "cors": {"compliant": True, "message": "bucket should not have CORS set"},
                    },
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
