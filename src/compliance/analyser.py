from abc import ABC, abstractmethod
from logging import Logger

from src.data.audit import Audit
from src.data.findings import Findings
from typing import Set


class Analyser(ABC):
    logger: Logger

    def __init__(self, logger: Logger, item_type: str):
        self.logger = logger
        self.item_type = item_type

    @abstractmethod
    def analyse(self, audit: Audit) -> Set[Findings]:
        """
        :param audit: an audit report
        :return: set of notifications for findings in the audit report
        """
