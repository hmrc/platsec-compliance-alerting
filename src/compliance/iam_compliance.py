from logging import Logger
from typing import Set, Dict, Any
from datetime import datetime, timedelta, timezone

from src.data.audit import Audit
from src.data.account import Account
from src.data.finding import Finding
from src.compliance.analyser import Analyser

ACCEPTABLE_MAX_AGE = timedelta(days=30)
AGE_VIOLATION_MESSAGE = f"key is older than {ACCEPTABLE_MAX_AGE.days} days"


class IamCompliance(Analyser):
    def __init__(self, logger: Logger) -> None:
        self._max_age = datetime.now(timezone.utc) - ACCEPTABLE_MAX_AGE
        super().__init__(logger=logger, item_type="iam_access_key")

    def analyse(self, audit: Audit) -> Set[Finding]:
        notifications = set()
        for report in audit.report:
            account = Account.from_dict(report["account"])
            for access_key in report["results"]["iam_access_keys"]:
                IamCompliance._convert_dates(access_key)
                notifications.add(
                    Finding(
                        account=account,
                        region_name=report["region"],
                        compliance_item_type=self.item_type,
                        item=access_key["id"],
                        findings=self._get_findings(access_key),
                        description=IamCompliance._make_description(access_key),
                    )
                )
        return notifications

    def _get_findings(self, access_key: Dict[str, Any]) -> Set[str]:
        findings = set()
        if access_key["created_datetime"] < self._max_age:
            findings.add(AGE_VIOLATION_MESSAGE)
        return findings

    @staticmethod
    def _make_description(access_key: Dict[str, Any]) -> str:
        now = datetime.now(timezone.utc)
        age = now - access_key["created_datetime"]
        user = access_key["user_name"]
        optional_s = "" if age.days == 1 else "s"
        conj = " and"
        last_used_suffix = ""
        if "last_used_datetime" in access_key:
            conj = ","
            last_used = now.date() - access_key["last_used_datetime"].date()
            last_used_suffix = " and was last used "
            if last_used.days == 0:
                last_used_suffix += "today"
            elif last_used.days == 1:
                last_used_suffix += "yesterday"
            else:
                last_used_suffix += f"{last_used.days} days ago"
        return f"this key is `{age.days} day{optional_s} old`{conj} belongs to `{user}`{last_used_suffix}"

    @staticmethod
    def _convert_dates(access_key: Dict[str, Any]) -> None:
        access_key["created_datetime"] = datetime.fromisoformat(access_key["created"])
        if "last_used" in access_key and access_key["last_used"]:
            access_key["last_used_datetime"] = datetime.fromisoformat(access_key["last_used"])
