from typing import Dict, Any

from src.data.account import Account
from src.data.findings import Findings


class GrantUserAccessLambda:
    Type: str = "GrantUserAccessLambda"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Findings:
        role_arn = message["roleArn"]
        target_account_id = role_arn.split(":")[4]
        account = Account(identifier=target_account_id)

        region = message["region"]
        role_arn = message["roleArn"]
        usernames = "\n  *  ".join(message["usernames"])
        hours = message["hours"]
        start_time = message["startTime"]
        end_time = message["endTime"]
        title = "Temporary access to user(s) granted"
        notification_text = (
            f"Access to `{role_arn}` has been granted for {hours} hour(s) to "
            f"the following users at {start_time}:\n  *  {usernames}\n"
            f"Access expires at {end_time}."
        )

        return Findings(
            compliance_item_type="grant_user_access_lambda",
            account=account,
            region_name=region,
            item=title,
            findings={notification_text},
        )
