from src.notifiers.notifier import Notifier


def test_notifier_abstract_methods() -> None:
    Notifier.__abstractmethods__ = set()

    assert not Notifier().apply_filters(payloads=set())
    assert not Notifier().apply_mappings(payloads=set())
    assert not Notifier().send(notifications=set())
