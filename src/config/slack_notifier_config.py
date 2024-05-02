from dataclasses import dataclass


@dataclass
class SlackNotifierConfig:
    api_v2_key: str
    api_url: str
    emoji: str
