vpc_report = [
    {
        "account": {"identifier": "111222333444", "name": "the-account"},
        "description": "audit VPC flow logs compliance",
        "results": {
            "vpcs": [{"id": "vpc-1a1a1a1a1a1a1a1a1"}],
            "enforcement_actions": [
                {"status": "applied", "description": "Delete delivery role for VPC flow log"},
                {
                    "status": "applied",
                    "description": "Create delivery role for VPC flow log",
                    "details": {"role_name": "the_delivery_role"},
                },
                {
                    "status": "applied",
                    "description": "Tag delivery role for VPC flow log",
                    "details": {"role_name": "the_delivery_role", "tags": [{"key": "a-key", "value": "a-value"}]},
                },
            ],
        },
    },
]
