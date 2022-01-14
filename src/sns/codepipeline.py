from typing import Dict, Any

from src.data.account import Account
from src.data.findings import Findings


class CodePipeline:

    Type: str = "CodePipeline Pipeline Execution State Change"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Findings:
        account = Account(identifier=message["account"])
        pipeline = message["detail"]["pipeline"]
        execution_id = message["detail"]["execution-id"]
        pipeline_status = message["detail"]["state"]
        finding = f"pipeline execution {execution_id} {pipeline_status}"
        return Findings(compliance_item_type="codepipeline", account=account, item=pipeline, findings={finding})
