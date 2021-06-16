import os

from unittest import TestCase
from unittest.mock import patch

from src.config import Config


class TestConfig(TestCase):
    @patch.dict(os.environ, {"CENTRAL_CHANNEL": "#the-central-channel"}, clear=True)
    def test_get_central_channel(self) -> None:
        self.assertEqual("#the-central-channel", Config().get_central_channel(self))
