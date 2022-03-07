from typing import Dict, Optional

from botocore.client import BaseClient

from logging import getLogger

from botocore.paginate import PageIterator

from src.data.account import Account


class AwsOrgClient:
    def __init__(self, boto_org: BaseClient):
        self._logger = getLogger(self.__class__.__name__)
        self._org = boto_org

    def get_account(self, account_id: str) -> Account:
        try:
            name = self._org.describe_account(AccountId=account_id)["Account"]["Name"]
            slack_handle = self._get_slack_handle(account_id)
        except Exception as e:
            name = "account not found"
            slack_handle = None
            self._logger.error(e)

        return Account(identifier=account_id, name=name, slack_handle=slack_handle or "owning-team-not-found")

    def _get_slack_handle(self, account_id: str) -> Optional[str]:
        paginator = self._org.get_paginator("list_tags_for_resource")
        page_iterator = paginator.paginate(ResourceId=account_id)
        tags = self.convert_to_tag_dict(page_iterator)

        return tags.get("team_slack_handle")

    def convert_to_tag_dict(self, page_iterator: PageIterator) -> Dict[str, str]:
        tags = {}
        for page in page_iterator:
            for tag in page["Tags"]:
                tags[tag["Key"]] = tag["Value"]

        return tags
