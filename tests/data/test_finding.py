from tests.test_types_generator import finding


def test_pagerduty_payload_equality() -> None:
    finding_a = finding(item="item-1")
    finding_b = finding(item="item-1")
    finding_c = finding(item="item-2")

    assert finding_a == finding_b
    assert finding_a != finding_c
    assert finding_a != ""
