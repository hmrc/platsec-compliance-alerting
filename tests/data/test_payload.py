from src.data.account import Account
from src.data.payload import Payload


def test_account_name() -> None:
    payload = Payload(
        description="",
        account=Account(identifier="123456789012", name="test-account", slack_handle=""),
        region_name="region",
    )
    assert payload.account_name == "test-account"
