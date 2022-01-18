import json
import os
from typing import Any

from src.sns.codebuild import CodeBuild


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("codebuild_event.json")["Records"][0]["Sns"]["Message"])

    finding = CodeBuild().create_finding(message)
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "codebuild"
    assert finding.item == "ua-test FAILED"
    assert len(finding.findings) == 1

    expected_logs_link = (
        "https://console.aws.amazon.com/cloudwatch/home"
        "?region=eu-west-2"
        "#logEvent:group=/aws/codebuild/ua-test;"
        "stream=7cf9f577-4069-4010-a467-f0640dfc0afb"
    )

    expected_build_link = (
        "https://eu-west-2.console.aws.amazon.com/codesuite/codebuild/123456789012/projects/"
        "ua-test/build/ua-test%3A7cf9f577-4069-4010-a467-f0640dfc0afb/?region=eu-west-2"
    )
    assert finding.findings == frozenset({f"<{expected_build_link}|build> <{expected_logs_link}|logs>"})


def load_json_resource(filename: str) -> Any:
    with open(os.path.join("tests", "resources", filename), "r") as json_file:
        resource = json.load(json_file)
    return resource
