import json
import os
from typing import Any

from src.sns.codebuild import CodeBuild


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("codebuild_event.json")["Records"][0]["Sns"]["Message"])

    finding = CodeBuild().create_finding(message)
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "codebuild"
    assert finding.item == "ua-test"
    assert len(finding.findings) == 1
    assert next(iter(finding.findings)) == "build arn:aws:codebuild:eu-west-2:123456789012:build/ua-test:7cf9f577-4069-4010-a467-f0640dfc0afb FAILED"


def load_json_resource(filename: str) -> Any:
    with open(os.path.join("tests", "resources", filename), "r") as json_file:
        resource = json.load(json_file)
    return resource
