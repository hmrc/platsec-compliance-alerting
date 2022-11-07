from typing import Any, Dict, Optional, Set

from src.compliance.analyser import Analyser
from src.data.account import Account
from src.data.audit import Audit
from src.data.findings import Findings


class VpcPeeringCompliance(Analyser):
    def analyse(self, audit: Audit) -> Set[Findings]:
        return {
            self._analyse_peering_connection(pcx, Account.from_dict(report["account"]), report["region"])
            for report in audit.report
            for pcx in report["results"]["vpc_peering_connections"]
        }

    def _analyse_peering_connection(self, pcx: Dict[str, Any], account: Account, region_name: str) -> Findings:
        return Findings(
            compliance_item_type="vpc_peering",
            item=pcx["id"],
            account=account,
            region_name=region_name,
            findings=self._check_for_unknown_accounts(pcx),
        )

    def _check_for_unknown_accounts(self, pcx: Dict[str, Any]) -> Set[str]:
        return set(filter(None, {self._is_unknown(pcx["requester"]), self._is_unknown(pcx["accepter"])}))

    def _is_unknown(self, acc: Dict[str, str]) -> Optional[str]:
        return f'vpc peering connection with unknown account {acc["identifier"]}' if acc["name"] == "unknown" else None
