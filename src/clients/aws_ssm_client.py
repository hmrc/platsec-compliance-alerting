from typing import Any, Dict, List

from botocore.client import BaseClient

from src.clients import boto_try


class AwsSsmClient:
    def __init__(self, boto_ssm: BaseClient):
        self._ssm = boto_ssm

    def get_parameter(self, parameter_name):
        pass