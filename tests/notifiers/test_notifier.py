from src.notifiers.notifier import Notifier


def test_notifier_abstract_methods() -> None:
    Notifier.__abstractmethods__ = set()

    assert None == Notifier().apply_filters(payloads=set())
    assert None == Notifier().apply_mappings(payloads=set())
    assert None == Notifier().send(notifications=set())
