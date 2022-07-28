from datetime import datetime, timezone
from typing import Set

from src.compliance.analyser import Analyser
from src.data.account import Account
from src.data.audit import Audit
from src.data.findings import Findings

MAX_AMI_AGE_DAYS: int = 90


class Ec2Compliance(Analyser):
    def analyse(self, audit: Audit) -> Set[Findings]:
        findings = set()
        for account in audit.report:
            for instance in account["results"]["ec2_instances"]:
                image_creation_date = instance.get("image_creation_date")
                if image_creation_date is None:
                    self.logger.warning(f"image_creation_date for '{instance['id']}' missing")
                    continue

                try:
                    image_creation_date = datetime.fromisoformat(image_creation_date)
                except ValueError:
                    self.logger.error(
                        f"image_creation_date '{instance['image_creation_date']}'"
                        f" for instance '{instance['id']}' does not match the date pattern"
                        f" YYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]"
                    )
                    continue

                image_creation_days_ago = (datetime.now(timezone.utc) - image_creation_date).days
                if image_creation_days_ago > MAX_AMI_AGE_DAYS:
                    findings.add(
                        Findings(
                            compliance_item_type="ami_creation_age",
                            account=Account.from_dict(account["account"]),
                            item=instance["component"],
                            findings={
                                f"Instance:  `{instance['id']}`",
                                f"Component: `{instance['component']}`",
                                f"Created:   `{image_creation_days_ago}` days ago. ",
                            },
                            description=f"Running image AMI created over {MAX_AMI_AGE_DAYS} days ago."
                            " The older an AMI becomes the higher the likelihood"
                            " the image is missing important security patches.",
                        )
                    )

        return findings
