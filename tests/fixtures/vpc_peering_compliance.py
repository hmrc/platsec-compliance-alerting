vpc_peering_audit = [
    {
        "account": {"identifier": "111222333444", "name": "account-1"},
        "region": "test-region-name",
        "description": "audit VPC peering connections",
        "results": {
            "vpc_peering_connections": [
                {
                    "id": "pcx-1a1a1a1a",
                    "accepter_owner_id": "121212121212",
                    "accepter_vpc_id": "vpc-88888888",
                    "requester_owner_id": "343434343434",
                    "requester_vpc_id": "vpc-55555555",
                    "status": "active",
                    "accepter": {"identifier": "111222333444", "name": "account-1"},
                    "requester": {"identifier": "343434343434", "name": "other-account"},
                },
                {
                    "id": "pcx-2b2b2b2b",
                    "accepter_owner_id": "121212121212",
                    "accepter_vpc_id": "vpc-88888888",
                    "requester_owner_id": "989898989898",
                    "requester_vpc_id": "vpc-9d9d9d9d",
                    "status": "active",
                    "accepter": {"identifier": "111222333444", "name": "account-1"},
                    "requester": {"identifier": "989898989898", "name": "unknown"},
                },
            ]
        },
    },
    {
        "account": {"identifier": "787878787878", "name": "account-2"},
        "region": "test-region-name",
        "description": "audit VPC peering connections",
        "results": {
            "vpc_peering_connections": [
                {
                    "id": "pcx-3c3c3c3c",
                    "accepter_owner_id": "787878787878",
                    "accepter_vpc_id": "vpc-99988877",
                    "requester_owner_id": "456456456456",
                    "requester_vpc_id": "vpc-7e7e7e7e",
                    "status": "active",
                    "accepter": {"identifier": "787878787878", "name": "account-2"},
                    "requester": {"identifier": "456456456456", "name": "unknown"},
                },
            ]
        },
    },
]
