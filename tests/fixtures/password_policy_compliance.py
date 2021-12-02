password_policy_report = [
    {
        "account": {"identifier": "979897989798", "name": "compliant-account"},
        "description": "audit password policy compliance",
        "results": {
            "password_policy": {
                "minimum_password_length": 24,
                "require_symbols": True,
                "require_numbers": True,
                "require_uppercase_chars": True,
                "require_lowercase_chars": True,
                "allow_users_to_change_password": True,
                "expire_passwords": True,
                "max_password_age": 30,
                "password_reuse_prevention": 10,
            },
            "enforcement_actions": [],
        },
    },
    {
        "account": {"identifier": "000000000000", "name": "bad-account"},
        "description": "audit password policy compliance",
        "results": {
            "password_policy": {
                "minimum_password_length": 5,
                "require_symbols": False,
                "require_numbers": True,
                "require_uppercase_chars": False,
                "require_lowercase_chars": False,
                "allow_users_to_change_password": False,
                "expire_passwords": False,
                "max_password_age": 9999,
                "password_reuse_prevention": 0,
            },
            "enforcement_actions": [
                {
                    "status": "applied",
                    "description": "Update IAM password policy",
                    "details": {
                        "password_policy": {
                            "minimum_password_length": 24,
                            "require_symbols": True,
                            "require_numbers": True,
                            "require_uppercase_chars": True,
                            "require_lowercase_chars": True,
                            "allow_users_to_change_password": True,
                            "expire_passwords": True,
                            "max_password_age": 30,
                            "password_reuse_prevention": 10,
                        }
                    },
                }
            ],
        },
    },
]
