from logging import getLogger

from src.compliance.vpc_peering_compliance import VpcPeeringCompliance

from tests.fixtures.vpc_peering_compliance import vpc_peering_audit
from tests.test_types_generator import account, create_audit, findings


acc_1 = account("111222333444", "account-1")
acc_2 = account("787878787878", "account-2")

finding_1 = findings(account=acc_1, compliance_item_type="vpc_peering", item="pcx-1a1a1a1a", findings=None)
finding_2 = findings(
    account=acc_1,
    compliance_item_type="vpc_peering",
    item="pcx-2b2b2b2b",
    findings={"vpc peering connection with unknown account 989898989898"},
)
finding_3 = findings(
    account=acc_2,
    compliance_item_type="vpc_peering",
    item="pcx-3c3c3c3c",
    findings={"vpc peering connection with unknown account 456456456456"},
)


def test_analyse_vpc_peering_audit() -> None:
    audit = create_audit(type="vpc_peering_audit.json", report=vpc_peering_audit)
    assert VpcPeeringCompliance(getLogger()).analyse(audit) == {finding_1, finding_2, finding_3}
