from typing import Dict, Any, Set, Sequence

from src.data.account import Account
from src.data.finding import Finding


class CodePipeline:
    Type: str = "CodePipeline Pipeline Execution State Change"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Finding:
        account = Account(identifier=message["account"])
        pipeline_name = message["detail"]["pipeline"]
        region = message["region"]
        pipeline_status = message["detail"]["state"]
        title = f"{pipeline_name} {pipeline_status}"
        execution_id = message["detail"]["execution-id"]
        link = CodePipeline.generate_pipeline_link(
            execution_id=execution_id, pipeline_name=pipeline_name, region=region
        )
        findings = CodePipeline.generate_error_messages(failed_actions=message["additionalAttributes"]["failedActions"])
        findings.add(link)
        findings.add(
            "This pipeline has failed and is blocking the path to production for new code, "
            "assume a role in the account and click the link to find out why."
        )

        return Finding(
            compliance_item_type="codepipeline",
            account=account,
            region_name=region,
            item=title,
            findings=findings,
        )

    @staticmethod
    def generate_error_messages(failed_actions: Sequence[Dict[str, str]]) -> Set[str]:
        return set(map(lambda e: e["additionalInformation"], failed_actions))

    @staticmethod
    def generate_pipeline_link(execution_id: str, pipeline_name: str, region: str) -> str:
        return (
            f"<https://{region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/"
            f"{pipeline_name}/executions/{execution_id}/visualization?region={region}|pipeline link>"
        )
