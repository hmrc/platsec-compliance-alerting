from typing import Dict, Any, Set

from src.data.account import Account
from src.data.findings import Findings


class CodePipeline:
    @staticmethod
    def event_to_findings(sns_event: Dict[str, Any]) -> Set[Findings]:
        return {CodePipeline.create_finding(record) for record in sns_event["Records"]}

    @staticmethod
    def create_finding(record: Dict[str, Any]) -> Findings:
        message = record["Sns"]["Message"]
        account = Account(identifier=message["account"])
        pipeline = message["detail"]["pipeline"]
        execution_id = message["detail"]["execution-id"]
        finding = f"pipeline execution {execution_id} failed"
        return Findings(compliance_item_type="codepipeline", account=account, item=pipeline, findings={finding})
