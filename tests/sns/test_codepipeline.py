import json

from src.sns.codepipeline import CodePipeline

from tests.sns import load_json_resource


def test_event_to_findings() -> None:
    message = json.loads(load_json_resource("codepipeline_event.json")["Records"][0]["Sns"]["Message"])

    finding = CodePipeline().create_finding(message)
    assert finding.account
    assert finding.account.identifier == "123456789012"
    assert finding.compliance_item_type == "codepipeline"
    assert finding.item == "test-codepipeline-ua FAILED"
    assert len(finding.findings) == 3
    expected_build_url = (
        "https://eu-west-2.console.aws.amazon.com/codesuite/codepipeline/pipelines/"
        "test-codepipeline-ua/"
        "executions/95bcd5b2-03b4-44ff-873b-8a95d57a24a0/visualization?region=eu-west-2"
    )

    assert f"<{expected_build_url}|pipeline link>" in finding.findings
    assert (
        "This pipeline has failed and is blocking the path to production for new code, "
        "assume a role in the account and click the link to find out why." in finding.findings
    )
    assert "The AWS CodeDeploy application test-codepipeline-ua does not exist" in finding.findings
