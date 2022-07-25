from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import List, Dict, Any, Optional

from src.compliance.ec2_compliance import Ec2Compliance
from src.data.account import Account
from tests.test_types_generator import create_audit


def test_ec2_analyse_returns_nothing_when_ami_new() -> None:
    good_account = Account("1234", "good_account")
    audit = create_audit(type="audit_ec2", report=[create_ec2_report(good_account, [create_instance_metadata()])])
    assert Ec2Compliance(getLogger()).analyse(audit) == set()


def test_ec2_analyse_returns_nothing_when_missing_ami_age() -> None:
    logger = getLogger()
    bad_account = Account("1235", "bad_account")
    metadata = create_instance_metadata()
    metadata["image_creation_date"] = "unknown"
    audit = create_audit(type="audit_ec2", report=[create_ec2_report(bad_account, [metadata])])

    assert len(Ec2Compliance(logger).analyse(audit)) == 0


def test_ec2_analyse_returns_findings_when_old_ami() -> None:
    good_account = Account("1234", "good_account")
    bad_account = Account("1235", "bad_account")
    audit = create_audit(
        type="audit_ec2",
        report=[
            create_ec2_report(good_account, [create_instance_metadata()]),
            create_ec2_report(
                bad_account,
                [
                    create_instance_metadata(image_creation_date=(datetime.now(timezone.utc) - timedelta(days=90))),
                    create_instance_metadata(image_creation_date=(datetime.now(timezone.utc) - timedelta(days=91))),
                    create_instance_metadata(image_creation_date=(datetime.now(timezone.utc) - timedelta(days=9999))),
                ],
            ),
        ],
    )
    assert len(Ec2Compliance(getLogger()).analyse(audit)) == 2


def create_instance_metadata(
    launch_time: Optional[datetime] = None, image_creation_date: Optional[datetime] = None
) -> Dict[str, Any]:
    if launch_time is None:
        launch_time = datetime.now(timezone.utc)
    if image_creation_date is None:
        image_creation_date = datetime.now(timezone.utc)
    return {
        "id": "i-12f312f312f31",
        "component": "test-component",
        "image_id": "ami-19034814134fa",
        "image_creation_date": image_creation_date.isoformat(),  # "2022-05-19T15:18:07+00:00",
        "launch_time": launch_time.isoformat(),  # "2022-05-19T15:18:07+00:00"
        "metadata_options_http_tokens": "optional",
    }


def create_ec2_report(account: Account, ec2_instances: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "account": {
            "identifier": account.identifier,
            "name": account.name,
        },
        "description": "audit EC2 instances",
        "results": {"ec2_instances": ec2_instances},
    }


def test_ec2_analise_unknoen_ami_age() -> None:
    pass
