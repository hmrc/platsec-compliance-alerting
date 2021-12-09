from typing import Dict, Any, Set
import json

from src.data.account import Account
from src.data.findings import Findings


class CodePipeline:
    @staticmethod
    def event_to_findings(sns_event: Dict[str, Any]) -> Set[Findings]:
        findings = [CodePipeline.create_finding(record) for record in sns_event["Records"]]
        return set(findings)

    @staticmethod
    def create_finding(record: Dict[str, Any]) -> Findings:
        message = json.loads(record["Sns"]["Message"])
        account = Account(identifier=message["account"])
        pipeline = message["detail"]["pipeline"]
        execution_id = message["detail"]["execution-id"]
        finding = f"pipeline execution {execution_id} failed"
        return Findings(compliance_item_type="codepipeline", account=account, item=pipeline, findings=set([finding]))
