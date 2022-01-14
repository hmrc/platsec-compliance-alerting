from typing import Dict, Any, Set
import json

from src.data.account import Account
from src.data.findings import Findings


class CodeBuild:
    Type: str = "CodeBuild Build State Change"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Findings:
        account = Account(identifier=message["account"])
        project_name = message["detail"]["project-name"]
        build_id = message["detail"]["build-id"]
        build_status = message["detail"]["build-status"]
        finding = f"build {build_id} {build_status}"
        return Findings(compliance_item_type="codebuild", account=account, item=project_name, findings={finding})
