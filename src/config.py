import os

from src.exceptions import MissingConfigException


class Config:
    @staticmethod
    def get_central_channel() -> str:
        try:
            return os.environ["CENTRAL_CHANNEL"]
        except KeyError:
            raise MissingConfigException("environment variable CENTRAL_CHANNEL")
