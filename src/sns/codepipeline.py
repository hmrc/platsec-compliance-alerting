from typing import Dict, Any

from src.data.account import Account
from src.data.findings import Findings


class CodePipeline:

    Type: str = "CodePipeline Pipeline Execution State Change"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Findings:
        account = Account(identifier=message["account"])
        pipline_name = message["detail"]["pipeline"]
        pipeline_status = message["detail"]["state"]
        title = f"{pipline_name} {pipeline_status}"
        execution_id = message["detail"]["execution-id"]
        finding = f"pipeline execution {execution_id}"
        return Findings(compliance_item_type="codepipeline", account=account, item=title, findings={finding})
