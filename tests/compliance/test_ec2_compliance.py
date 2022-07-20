from src.compliance.ec2_compliance import Ec2Compliance
from tests.test_types_generator import create_audit


def test_ec2_analyse() -> None:
    audit = create_audit(type="audit_ec2", report=[])
    assert Ec2Compliance().analyse(audit) == set()
