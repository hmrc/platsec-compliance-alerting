from dataclasses import dataclass


@dataclass
class SlackNotifierConfig:
    username: str
    token: str
    api_url: str
