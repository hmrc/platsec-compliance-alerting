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

    # {
    #     "region": "eu-west-2",
    #     "consoleLink": "https://console.aws.amazon.com/codesuite/codepipeline/pipelines/compliance-alerting/view?region=eu-west-2",
    #     "approval": {
    #         "pipelineName": "compliance-alerting", "stageName": "Approve_Production", "actionName": "Approve_Production", "token": "a7b432e8-3c05-4efd-b9a6-6c0e4fa85e39",
    #         "expires": "2025-11-27T10:46Z", "externalEntityLink": "https://github.com/org/repo/commit/abcde12345",
    #         "approvalReviewLink": "https://console.aws.amazon.com/codesuite/codepipeline/pipelines/repo/view?region=eu-west-2#/Approve_Production/Approve_Production/approve/uuid4",
    #         "customData": "commit message"
    #     }
    # }
    @staticmethod
    def create_approval_finding(message: Dict[str, Any], ci_account_id: str) -> Finding:
        account = Account(identifier=ci_account_id)
        pipeline_name = message["approval"]["pipelineName"]
        stage_name = message["approval"]["stageName"]

        findings = set()
        findings.add(f"<{message['consoleLink']}|pipeline link>")
        findings.add(f"The AWS CodePipeline {pipeline_name} pipeline is awaiting manual approval.")

        return Finding(
            compliance_item_type="codepipeline",
            account=account,
            region_name=message["region"],
            item=f"{pipeline_name} {stage_name}",
            description=f"Manual approval for {pipeline_name} pipeline",
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
