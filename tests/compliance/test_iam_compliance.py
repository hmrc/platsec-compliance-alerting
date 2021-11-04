from datetime import datetime, timedelta
from typing import List, Dict, Any
from tests.test_types_generator import create_account, create_audit

from src.compliance.iam_compliance import IamCompliance
from src.data.account import Account
from src.data.findings import Findings

EXPECTED_OLD_KEY_VIOLATION = "key is older than 30 days"


def test_no_violations():
    good_keys = [
        {
            "id": "key1_id",
            "user_name": "test_user1",
            "created": datetime.now() - timedelta(days=29),
        },
        {
            "id": "key2_id",
            "user_name": "test_user2",
            "created": datetime.now() - timedelta(days=10),
            "last_used": datetime.now() - timedelta(days=2),
        },
    ]
    account = create_account()
    audit = create_audit([(create_account_report(account, good_keys))])

    notifications = IamCompliance().analyse(audit)

    assert sorted(notifications, key=lambda x: x.item) == [
        Findings(
            account=account,
            item="key1_id",
            findings=set(),
            description="this key is 29 days old and belongs to test_user1",
        ),
        Findings(
            account=account,
            item="key2_id",
            findings=set(),
            description="this key is 10 days old, belongs to test_user2 and was last used 2 days ago",
        ),
    ]


def test_keys_older_than_30_days():
    keys_account1 = [
        {
            "id": "key1_id",
            "user_name": "test_user1_old",
            "created": datetime.now() - timedelta(days=31),
        },
        {
            "id": "key2_id",
            "user_name": "test_user2_old",
            "created": datetime.now() - timedelta(days=100),
            "last_used": datetime.now(),
        },
    ]
    keys_account2 = [
        {
            "id": "key3_id",
            "user_name": "test_user3_good",
            "created": datetime.now() - timedelta(days=1),
        },
        {
            "id": "key4_id",
            "user_name": "test_user4_old",
            "created": datetime.now() - timedelta(days=999),
            "last_used": datetime.now() - timedelta(days=1),
        },
    ]
    account1 = create_account()
    account2 = create_account()
    audit = create_audit(
        [(create_account_report(account1, keys_account1)), (create_account_report(account2, keys_account2))]
    )

    notifications = IamCompliance().analyse(audit)

    assert sorted(notifications, key=lambda x: x.item) == [
        Findings(
            account=account1,
            item="key1_id",
            findings={EXPECTED_OLD_KEY_VIOLATION},
            description="this key is 31 days old and belongs to test_user1_old",
        ),
        Findings(
            account=account1,
            item="key2_id",
            findings={EXPECTED_OLD_KEY_VIOLATION},
            description="this key is 100 days old, belongs to test_user2_old and was last used today",
        ),
        Findings(
            account=account2,
            item="key3_id",
            findings=set(),
            description="this key is 1 day old and belongs to test_user3_good",
        ),
        Findings(
            account=account2,
            item="key4_id",
            findings={EXPECTED_OLD_KEY_VIOLATION},
            description="this key is 999 days old, belongs to test_user4_old and was last used yesterday",
        ),
    ]


def create_account_report(account: Account, access_keys: List[Dict[str, Any]]):
    dates_as_strings = []
    for access_key in access_keys:
        key = {
            "id": access_key["id"],
            "user_name": access_key["user_name"],
            "created": access_key["created"].isoformat(),
        }
        if "last_used" in access_key:
            key["last_used"] = access_key["last_used"].isoformat()

        dates_as_strings.append(key)
    return {
        "account": {
            "identifier": account.identifier,
            "name": account.name,
        },
        "description": "audit_iam",
        "results": {"iam_access_keys": dates_as_strings},
    }