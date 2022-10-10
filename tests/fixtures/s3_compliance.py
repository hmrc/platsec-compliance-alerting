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
                        "tagging": {"compliant": True, "message": "bucket should have tags for expiry and sensitivity"},
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
                            "compliant": True,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "acl": {"compliant": True, "message": "bucket should not have ACL set"},
                        "encryption": {"compliant": False, "message": "bucket should be encrypted"},
                        "logging": {"compliant": False, "message": "bucket should have logging enabled"},
                        "versioning": {"compliant": True, "message": "bucket should have versioning enabled"},
                        "mfa_delete": {"compliant": True, "message": "MFA delete should be disabled"},
                        "tagging": {
                            "compliant": False,
                            "message": "bucket should have tags for expiry and sensitivity",
                        },
                        "lifecycle": {"compliant": True, "message": "bucket should have a lifecycle configuration set"},
                        "cors": {"compliant": True, "message": "bucket should not have CORS set"},
                    },
                    "encryption": {"enabled": False},
                    "secure_transport": {},
                    "public_access_block": {"enabled": True},
                    "data_tagging": {"expiry": "1-week", "sensitivity": "unset"},
                    "logging": {"enabled": False},
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
                    "compliancy": {
                        "content_deny": {
                            "compliant": False,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "logging": {"compliant": False, "message": "bucket should have logging enabled"},
                        "public_access_block": {"compliant": False, "message": "bucket should not allow public access"},
                        "secure_transport": {
                            "compliant": False,
                            "message": "bucket should have a resource policy with secure transport enforced",
                        },
                        "tagging": {
                            "compliant": False,
                            "message": "bucket should have tags for expiry and sensitivity",
                        },
                        "versioning": {"compliant": True, "message": "bucket should have versioning enabled"},
                        "kms_key": {"compliant": False, "message": "bucket kms key should have rotation enabled"},
                    },
                    "encryption": {"enabled": True},
                    "secure_transport": {},
                    "public_access_block": {"enabled": False},
                    "data_tagging": {"expiry": "unset", "sensitivity": "high"},
                    "logging": {},
                    "kms_key": {"rotation_enabled": False},
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
                        "tagging": {"compliant": True, "message": "bucket should have tags for expiry and sensitivity"},
                        "lifecycle": {"compliant": True, "message": "bucket should have a lifecycle configuration set"},
                        "cors": {"compliant": True, "message": "bucket should not have CORS set"},
                    },
                    "encryption": {"enabled": True},
                    "secure_transport": {"enabled": True},
                    "public_access_block": {"enabled": True},
                    "data_tagging": {"expiry": "1-week", "sensitivity": "high"},
                    "content_deny": {"enabled": True},
                    "logging": {"enabled": True},
                    "kms_key": {"rotation_enabled": True},
                },
            ]
        },
    },
    {
        "account": {
            "identifier": "555666777444",
            "name": "an-account",
        },
        "results": {
            "buckets": [
                {
                    "name": "bad-bucket-low-sensitivity",
                    "compliancy": {
                        "content_deny": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "acl": {"compliant": True, "message": "bucket should not have ACL set"},
                        "encryption": {"compliant": False, "message": "bucket should be encrypted"},
                        "logging": {"compliant": False, "message": "bucket should have logging enabled"},
                        "public_access_block": {"compliant": False, "message": "bucket should not allow public access"},
                        "secure_transport": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with secure transport enforced",
                        },
                        "versioning": {"compliant": True, "message": "bucket should have versioning enabled"},
                        "mfa_delete": {"compliant": True, "message": "MFA delete should be disabled"},
                        "kms_key": {"compliant": True, "message": "bucket kms key should have rotation enabled"},
                        "tagging": {
                            "compliant": False,
                            "message": "bucket should have tags for expiry and sensitivity",
                        },
                        "lifecycle": {"compliant": True, "message": "bucket should have a lifecycle configuration set"},
                        "cors": {"compliant": True, "message": "bucket should not have CORS set"},
                    },
                    "encryption": {"enabled": False},
                    "secure_transport": {},
                    "public_access_block": {"enabled": False},
                    "data_tagging": {"expiry": "unset", "sensitivity": "low"},
                    "logging": {},
                    "kms_key": {"rotation_enabled": False},
                },
            ]
        },
    },
    {
        "account": {
            "identifier": "998877665544",
            "name": "yet-another-account",
        },
        "results": {
            "buckets": [
                {
                    "name": "logging-skipped-good-bucket",
                    "compliancy": {
                        "content_deny": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "acl": {"compliant": True, "message": "bucket should not have ACL set"},
                        "encryption": {"compliant": True, "message": "bucket should be encrypted"},
                        "logging": {
                            "compliant": False,
                            "skipped": True,
                            "message": "bucket should have logging enabled",
                        },
                        "public_access_block": {"compliant": True, "message": "bucket should not allow public access"},
                        "secure_transport": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with secure transport enforced",
                        },
                        "versioning": {"compliant": True, "message": "bucket should have versioning enabled"},
                        "mfa_delete": {"compliant": True, "message": "MFA delete should be disabled"},
                        "kms_key": {"compliant": True, "message": "bucket kms key should have rotation enabled"},
                        "tagging": {"compliant": True, "message": "bucket should have tags for expiry and sensitivity"},
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
                    "name": "logging-skipped-bad-bucket",
                    "compliancy": {
                        "content_deny": {
                            "compliant": True,
                            "message": "bucket should have a resource policy with a default deny action",
                        },
                        "acl": {"compliant": True, "message": "bucket should not have ACL set"},
                        "encryption": {"compliant": False, "message": "bucket should be encrypted"},
                        "logging": {
                            "compliant": False,
                            "skipped": True,
                            "message": "bucket should have logging enabled",
                        },
                        "versioning": {"compliant": True, "message": "bucket should have versioning enabled"},
                        "mfa_delete": {"compliant": True, "message": "MFA delete should be disabled"},
                        "tagging": {
                            "compliant": False,
                            "message": "bucket should have tags for expiry and sensitivity",
                        },
                        "lifecycle": {"compliant": True, "message": "bucket should have a lifecycle configuration set"},
                        "cors": {"compliant": True, "message": "bucket should not have CORS set"},
                    },
                    "encryption": {"enabled": False},
                    "secure_transport": {},
                    "public_access_block": {"enabled": True},
                    "data_tagging": {"expiry": "1-week", "sensitivity": "unset"},
                    "logging": {"enabled": False},
                    "kms_key": {"rotation_enabled": False},
                },
            ]
        },
    },
]
