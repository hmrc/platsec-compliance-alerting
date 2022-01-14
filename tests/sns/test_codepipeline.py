import json
import os
from typing import Any

from src.sns.codepipeline import CodePipeline


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("codepipeline_event.json")["Records"][0]["Sns"]["Message"])

    finding = CodePipeline().create_finding(message)
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "codepipeline"
    assert finding.item == "test-codepipeline-ua"
    assert len(finding.findings) == 1
    assert next(iter(finding.findings)) == "pipeline execution 95bcd5b2-03b4-44ff-873b-8a95d57a24a0 FAILED"


def load_json_resource(filename: str) -> Any:
    with open(os.path.join("tests", "resources", filename), "r") as json_file:
        resource = json.load(json_file)
    return resource
