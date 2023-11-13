from datetime import datetime, timezone
from typing import Set, Dict, Any
from logging import Logger

from src.compliance.analyser import Analyser
from src.data.account import Account
from src.data.audit import Audit
from src.data.finding import Finding

MAX_AMI_AGE_DAYS: int = 90


class Ec2Compliance(Analyser):
    def __init__(self, logger: Logger) -> None:
        super().__init__(logger=logger, item_type="ami_creation_age")

    def analyse(self, audit: Audit) -> Set[Finding]:
        findings = set()
        for account in audit.report:
            for instance in account["results"]["ec2_instances"]:
                image_creation_date = instance.get("image_creation_date")
                if image_creation_date is None:
                    # image_creation_date will be missing if the AMI can no longer be found.
                    # Here we assume it has been deleted
                    try:
                        launch_time = datetime.fromisoformat(instance["launch_time"])
                    except ValueError:
                        self.log_date_parse_error(field_name="launch_time", instance=instance)
                        continue
                    launch_time_days_ago = (datetime.now(timezone.utc) - launch_time).days
                    if launch_time_days_ago > MAX_AMI_AGE_DAYS:
                        findings.add(
                            self.create_ami_age_finding(
                                account=account,
                                instance=instance,
                                findings={
                                    f"Instance:  `{instance['id']}`",
                                    f"Component: `{instance['component']}`",
                                    f"Started:   `{launch_time_days_ago}` days ago.",
                                },
                                description=f"Running image AMI has been deleted"
                                f" but instance has been running for over {MAX_AMI_AGE_DAYS} days!"
                                " The older an instance becomes the higher the likelihood"
                                " the image is missing important security patches.",
                            )
                        )
                else:
                    try:
                        image_creation_date = datetime.fromisoformat(image_creation_date)
                    except ValueError:
                        self.log_date_parse_error(field_name="image_creation_date", instance=instance)
                        continue

                    image_creation_days_ago = (datetime.now(timezone.utc) - image_creation_date).days
                    if image_creation_days_ago > MAX_AMI_AGE_DAYS:
                        findings.add(
                            self.create_ami_age_finding(
                                account=account,
                                instance=instance,
                                findings={
                                    f"Instance:  `{instance['id']}`",
                                    f"Component: `{instance['component']}`",
                                    f"Created:   `{image_creation_days_ago}` days ago.",
                                },
                                description=f"Running image AMI created over {MAX_AMI_AGE_DAYS} days ago."
                                " The older an AMI becomes the higher the likelihood"
                                " the image is missing important security patches.",
                            )
                        )

        return findings

    @staticmethod
    def create_ami_age_finding(
        account: Dict[str, Any], instance: Dict[str, Any], findings: set[str], description: str
    ) -> Finding:
        return Finding(
            compliance_item_type="ami_creation_age",
            account=Account.from_dict(account["account"]),
            region_name=account["region"],
            item=instance["component"],
            findings=findings,
            description=description,
        )

    def log_date_parse_error(self, field_name: str, instance: Dict[str, str]) -> None:
        self.logger.error(
            f"{field_name} '{instance.get(field_name)}'"
            f" for instance '{instance['id']}' does not match the date pattern"
            f" YYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]"
        )
