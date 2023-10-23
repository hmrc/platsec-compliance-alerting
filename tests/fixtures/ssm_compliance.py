ssm_audit_report = [
    {
        "account": {"identifier": "111222333444", "name": "account-1"},
        "region": "test-region-name",
        "description": "Audit SSM RunShell Document",
        "results": {
            "documents": [
                {
                    "name": "SSM-SessionManagerRunShell",
                    "compliancy": {
                        "s3BucketName": {
                            "compliant": True,
                            "message": "S3 bucket name should be mdtp-ssm-session-manager-audit-logs",
                        },
                        "s3EncryptionEnabled": {"compliant": True, "message": "S3 encryption should be enabled"},
                        "maxSessionDuration": {
                            "compliant": True,
                            "message": "maxSessionDuration should be less than or equal to 120 mins",
                        },
                        "shellProfile": {"compliant": True, "message": "shellProfile should match expected config"},
                    },
                }
            ]
        },
    }
]

ssm_audit_report_non_compliant_s3_config_items = [
    {
        "account": {"identifier": "111222333444", "name": "account-1"},
        "region": "test-region-name",
        "description": "Audit SSM RunShell Document",
        "results": {
            "documents": [
                {
                    "name": "SSM-SessionManagerRunShell",
                    "compliancy": {
                        "s3BucketName": {
                            "compliant": False,
                            "message": "S3 bucket name should be mdtp-ssm-session-manager-audit-logs",
                        },
                        "s3EncryptionEnabled": {"compliant": False, "message": "S3 encryption should be enabled"},
                        "maxSessionDuration": {
                            "compliant": True,
                            "message": "maxSessionDuration should be less than or equal to 120 mins",
                        },
                        "shellProfile": {"compliant": True, "message": "shellProfile should match expected config"},
                    },
                }
            ]
        },
    }
]

ssm_audit_report_non_compliant_max_session_duration_shell_profile = [
    {
        "account": {"identifier": "111222333444", "name": "account-1"},
        "region": "test-region-name",
        "description": "Audit SSM RunShell Document",
        "results": {
            "documents": [
                {
                    "name": "SSM-SessionManagerRunShell",
                    "compliancy": {
                        "s3BucketName": {
                            "compliant": True,
                            "message": "S3 bucket name should be mdtp-ssm-session-manager-audit-logs",
                        },
                        "s3EncryptionEnabled": {"compliant": True, "message": "S3 encryption should be enabled"},
                        "maxSessionDuration": {
                            "compliant": False,
                            "message": "maxSessionDuration should be less than or equal to 120 mins",
                        },
                        "shellProfile": {"compliant": False, "message": "shellProfile should match expected config"},
                    },
                }
            ]
        },
    }
]
