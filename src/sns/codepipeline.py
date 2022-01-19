from typing import Dict, Any

from src.data.account import Account
from src.data.findings import Findings


class CodePipeline:

    Type: str = "CodePipeline Pipeline Execution State Change"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Findings:
        account = Account(identifier=message["account"])
        pipeline_name = message["detail"]["pipeline"]
        region = message["region"]
        pipeline_status = message["detail"]["state"]
        title = f"{pipeline_name} {pipeline_status}"
        execution_id = message["detail"]["execution-id"]
        link = CodePipeline.generate_pipeline_link(
            execution_id=execution_id, pipeline_name=pipeline_name, region=region
        )
        return Findings(
            compliance_item_type="codepipeline",
            account=account,
            item=title,
            findings={link},
        )

    @staticmethod
    def generate_pipeline_link(execution_id: str, pipeline_name: str, region: str):
        return (
            f"<https://{region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/"
            f"{pipeline_name}/executions/{execution_id}/visualization?region={region}|pipeline link>"
        )
