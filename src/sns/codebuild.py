import urllib
from typing import Dict, Any

from src.data.account import Account
from src.data.finding import Finding


class CodeBuild:
    Type: str = "CodeBuild Build State Change"

    @staticmethod
    def create_finding(message: Dict[str, Any]) -> Finding:
        account = Account(identifier=message["account"])
        region = message["region"]
        project_name = message["detail"]["project-name"]
        build_id = message["detail"]["build-id"]
        build_status = message["detail"]["build-status"]
        title = f"{project_name} {build_status}"
        logs_url = message["detail"]["additional-information"]["logs"]["deep-link"]

        codebuild_url = CodeBuild.generate_codebuild_url(
            account_id=account.identifier, build_id=build_id, project_name=project_name, region=region
        )

        return Finding(
            compliance_item_type="codebuild",
            account=account,
            region_name=region,
            item=title,
            findings={f"<{codebuild_url}|build> | <{logs_url}|logs>"},
        )

    @staticmethod
    def generate_codebuild_url(account_id: str, build_id: str, project_name: str, region: str) -> str:
        build_url_suffix = urllib.parse.quote(build_id.split("build/")[-1])
        return (
            f"https://{region}.console.aws.amazon.com/codesuite/codebuild/"
            f"{account_id}/projects/{project_name}/build/{build_url_suffix}/?region={region}"
        )
