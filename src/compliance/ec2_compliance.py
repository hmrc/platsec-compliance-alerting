from datetime import datetime, timezone
from logging import Logger
from typing import Set

from src.compliance.analyser import Analyser
from src.data.account import Account
from src.data.audit import Audit
from src.data.findings import Findings

MAX_AMI_AGE_DAYS: int = 90


class Ec2Compliance(Analyser):
    def analyse(self, logger: Logger, audit: Audit) -> Set[Findings]:
        findings = set()
        for account in audit.report:
            for instance in account["results"]["ec2_instances"]:
                try:
                    image_creation_date = datetime.fromisoformat(instance["image_creation_date"])
                except ValueError:
                    logger.error(
                        f"'{instance['image_creation_date']}'does not match the date pattern"
                        f" YYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]"
                    )
                    continue

                image_creation_days_ago = (datetime.now(timezone.utc) - image_creation_date).days
                if image_creation_days_ago > MAX_AMI_AGE_DAYS:
                    findings.add(
                        Findings(
                            account=Account.from_dict(account["account"]),
                            compliance_item_type="ami_creation_age",
                            item=instance["id"],
                            findings={f"Running image AMI created over {MAX_AMI_AGE_DAYS} days ago"},
                            description=f"Instance'{instance['id']}' for component '{instance['component']}'"
                            f" was created {image_creation_days_ago} days ago. "
                            "This increases the likelihood the image is missing important security patches",
                        )
                    )

        return findings
