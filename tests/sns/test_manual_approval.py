import json

from src.sns.codepipeline import CodePipeline

from tests.sns import load_json_resource


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("codepipeline_approval_event.json")["Records"][0]["Sns"]["Message"])

    finding = CodePipeline().create_approval_finding(message)
    assert finding.account
    assert finding.account.identifier == "987972305662"
    assert finding.compliance_item_type == "codepipeline"
    assert finding.item == "test-pipeline Approve_Production"
    assert len(finding.findings) == 2
    expected_build_url = (
        "https://console.aws.amazon.com/codesuite/codepipeline/pipelines/compliance-alerting/view?region=eu-west-2"
    )

    assert f"<{expected_build_url}|pipeline link>" in finding.findings

    assert "The AWS CodePipeline test-pipeline pipeline is awaiting manual approval." in finding.findings
