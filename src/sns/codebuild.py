from typing import Dict, Any, Set
import json

from src.data.account import Account
from src.data.findings import Findings


class CodeBuild:
    @staticmethod
    def event_to_findings(sns_event: Dict[str, Any]) -> Set[Findings]:
        return {CodeBuild.create_finding(record) for record in sns_event["Records"]}

    @staticmethod
    def create_finding(record: Dict[str, Any]) -> Findings:
        message = json.loads(record["Sns"]["Message"])
        account = Account(identifier=message["account"])
        project_name = message["detail"]["project-name"]
        build_id = message["detail"]["build-id"]
        build_status = message["detail"]["build-status"]
        finding = f"build {build_id} {build_status}"
        return Findings(compliance_item_type="codebuild", account=account, item=project_name, findings={finding})
