from tests.test_types_generator import _pagerduty_payload


def test_pagerduty_payload_equality() -> None:
    payload_a = _pagerduty_payload(source="444555666777", component="component-a")
    payload_b = _pagerduty_payload(source="444555666777", component="component-a")
    payload_c = _pagerduty_payload(source="999888777666", component="component-a")

    assert payload_a == payload_b
    assert payload_a != payload_c
    assert payload_a != ""
