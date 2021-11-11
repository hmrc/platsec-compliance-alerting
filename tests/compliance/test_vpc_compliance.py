from tests.test_types_generator import create_audit

from src.compliance.vpc_compliance import VpcCompliance


def test_analyse() -> None:
    VpcCompliance().analyse(
        create_audit(
            report=[{"account": {"identifier": "1234", "name": "bla"}, "results": {"vpcs": [{"id": "1"}]}}], type="vpc"
        )
    )
