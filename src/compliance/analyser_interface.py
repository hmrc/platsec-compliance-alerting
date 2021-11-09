from abc import ABC, abstractmethod
from src.data.audit import Audit
from src.data.findings import Findings
from typing import Set


class AnalyserInterface(ABC):
    @abstractmethod
    def analyse(self, audit: Audit) -> Set[Findings]:
        """
        :param audit: an audit report
        :return: set of notifications for findings in the audit report
        """
