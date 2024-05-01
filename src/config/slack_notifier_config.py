from dataclasses import dataclass


@dataclass
class SlackNotifierConfig:
    username: str
    api_v2_key: str
    api_url: str
