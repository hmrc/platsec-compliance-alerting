from botocore.client import BaseClient

from src.clients import boto_try


class AwsSsmClient:
    def __init__(self, boto_ssm: BaseClient):
        self._ssm = boto_ssm

    def get_parameter(self, parameter_name: str) -> str:
        return boto_try(
            lambda: self._ssm.get_parameter(Name=parameter_name, WithDecryption=True)["Parameter"]["Value"],
            f"failed to get parameter {parameter_name}",
        )
