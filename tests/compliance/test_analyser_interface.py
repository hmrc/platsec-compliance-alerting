from unittest import TestCase
from unittest.mock import patch
from src.data.audit import Audit

from src.compliance.analyser_interface import AnalyserInterface


class TestAnalyserInterface(TestCase):
    @patch.multiple(AnalyserInterface, __abstractmethods__=set())
    def test_interface_analyse(self) -> None:
        self.assertIsNone(AnalyserInterface().analyse(Audit))
