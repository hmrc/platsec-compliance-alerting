from abc import ABC, abstractmethod
from logging import Logger

from src.data.audit import Audit
from src.data.findings import Findings
from typing import Set


class Analyser(ABC):
    logger: Logger

    def __init__(self, logger: Logger):
        self.logger = logger

    @abstractmethod
    def analyse(self, audit: Audit) -> Set[Findings]:
        """
        :param audit: an audit report
        :return: set of notifications for findings in the audit report
        """
