from abc import ABC, abstractmethod
from logging import Logger

from src.data.audit import Audit
from src.data.findings import Findings
from typing import Set


class Analyser(ABC):
    @abstractmethod
    def analyse(self, logger: Logger, audit: Audit) -> Set[Findings]:
        """
        :param logger:
        :param audit: an audit report
        :return: set of notifications for findings in the audit report
        """
