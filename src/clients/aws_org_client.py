from botocore.client import BaseClient

from logging import getLogger

from src.data.account import Account


class AwsOrgClient:
    def __init__(self, boto_org: BaseClient):
        self._logger = getLogger(self.__class__.__name__)
        self._org = boto_org

    def get_account_details(self, account_id: str) -> Account:
        try:
            name = self._org.describe_account(AccountId=account_id)["Account"]["Name"]
        except Exception as e:
            name = "account not found"
            self._logger.error(e)

        return Account(identifier=account_id, name=name)
