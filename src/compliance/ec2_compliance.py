from typing import Set

from src.compliance.analyser import Analyser
from src.data.audit import Audit
from src.data.findings import Findings


class Ec2Compliance(Analyser):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return set()
