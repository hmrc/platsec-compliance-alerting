from datetime import datetime, timedelta
from logging import getLogger
from typing import List, Dict, Any
from zoneinfo import ZoneInfo

from tests.test_types_generator import create_account, create_audit

from src.compliance.iam_compliance import IamCompliance
from src.data.account import Account
from src.data.findings import Findings

EXPECTED_OLD_KEY_VIOLATION = "key is older than 30 days"
UTC = ZoneInfo("UTC")


def test_no_violations() -> None:
    good_keys = [
        {
            "id": "key1_id",
            "user_name": "test_user1",
            "created": datetime.now(tz=UTC) - timedelta(days=29),
        },
        {
            "id": "key2_id",
            "user_name": "test_user2",
            "created": datetime.now(tz=UTC) - timedelta(days=10),
            "last_used": datetime.now(tz=UTC) - timedelta(days=2),
        },
    ]
    account = create_account()
    audit = create_audit([(create_account_report(account, good_keys))])

    notifications = IamCompliance(getLogger()).analyse(audit)

    assert sorted(notifications, key=lambda x: x.item) == [
        Findings(
            account=account,
            region_name="test-region-name",
            compliance_item_type="iam_access_key",
            item="key1_id",
            findings=set(),
            description="this key is `29 days old` and belongs to `test_user1`",
        ),
        Findings(
            account=account,
            region_name="test-region-name",
            compliance_item_type="iam_access_key",
            item="key2_id",
            findings=set(),
            description="this key is `10 days old`, belongs to `test_user2` and was last used 2 days ago",
        ),
    ]


def test_keys_older_than_30_days() -> None:
    keys_account1 = [
        {
            "id": "key1_id",
            "user_name": "test_user1_old",
            "created": datetime.now(tz=UTC) - timedelta(days=31),
        },
        {
            "id": "key2_id",
            "user_name": "test_user2_old",
            "created": datetime.now(tz=UTC) - timedelta(days=100),
            "last_used": datetime.now(tz=UTC),
        },
    ]
    keys_account2 = [
        {
            "id": "key3_id",
            "user_name": "test_user3_good",
            "created": datetime.now(tz=UTC) - timedelta(days=1),
        },
        {
            "id": "key4_id",
            "user_name": "test_user4_old",
            "created": datetime.now(tz=UTC) - timedelta(days=999),
            "last_used": datetime.now(tz=UTC) - timedelta(days=1),
        },
    ]
    account1 = create_account()
    account2 = create_account()
    audit = create_audit(
        [(create_account_report(account1, keys_account1)), (create_account_report(account2, keys_account2))]
    )

    notifications = IamCompliance(getLogger()).analyse(audit)

    assert sorted(notifications, key=lambda x: x.item) == [
        Findings(
            account=account1,
            region_name="test-region-name",
            compliance_item_type="iam_access_key",
            item="key1_id",
            findings={EXPECTED_OLD_KEY_VIOLATION},
            description="this key is `31 days old` and belongs to `test_user1_old`",
        ),
        Findings(
            account=account1,
            region_name="test-region-name",
            compliance_item_type="iam_access_key",
            item="key2_id",
            findings={EXPECTED_OLD_KEY_VIOLATION},
            description="this key is `100 days old`, belongs to `test_user2_old` and was last used today",
        ),
        Findings(
            account=account2,
            region_name="test-region-name",
            compliance_item_type="iam_access_key",
            item="key3_id",
            findings=set(),
            description="this key is `1 day old` and belongs to `test_user3_good`",
        ),
        Findings(
            account=account2,
            region_name="test-region-name",
            compliance_item_type="iam_access_key",
            item="key4_id",
            findings={EXPECTED_OLD_KEY_VIOLATION},
            description="this key is `999 days old`, belongs to `test_user4_old` and was last used yesterday",
        ),
    ]


def create_account_report(account: Account, access_keys: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        "region": "test-region-name",
        "description": "audit_iam",
        "results": {"iam_access_keys": dates_as_strings},
    }
