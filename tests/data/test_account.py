from unittest import TestCase

from tests.test_types_generator import account


class TestAccount(TestCase):
    def test_account_eq(self) -> None:
        self.assertEqual(account(identifier="1234", name="banana"), account(identifier="1234", name="strawberry"))

    def test_account_not_eq(self) -> None:
        self.assertNotEqual(account(identifier="1234", name="cherry"), account(identifier="5678", name="cherry"))
        self.assertNotEqual(account(identifier="1234", name="cherry"), "something")
