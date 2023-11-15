from src.data.notification import Notification


def test_notification_to_dict() -> None:
    Notification.__abstractmethods__ = set()

    assert None == Notification().to_dict()
