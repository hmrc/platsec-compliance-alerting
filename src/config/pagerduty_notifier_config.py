from dataclasses import dataclass


@dataclass
class PagerDutyNotifierConfig:
    service: str
    routing_key: str
    api_url: str
