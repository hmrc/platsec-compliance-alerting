from dataclasses import dataclass
from typing import Any, Dict, List

from src.data.notification import Notification


@dataclass
class SlackMessage(Notification):
    channels: List[str]
    heading: Dict[str, Any]
    title: str
    text: str
    color: str

    def __init__(self, channels: List[str], heading: Dict[str, Any], title: str, text: str, color: str):
        self.channels = list(filter(None, channels))
        self.heading = heading
        self.title = title
        self.text = text
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channelLookup": {
                "by": "slack-channel",
                "slackChannels": self.channels,
            },
            "displayName": self.title,
            "emoji": ":this-is-fine:",
            "blocks": [
                self.heading,
                {"type": "divider"},
                # {"type": "section", "text": {"type": "mrkdwn", "text": self.text}},   # FOR FUTURE USE AS
                # Attachments block is considered legacy by Slack and may be deprecated
            ],
            "text": "",
            "attachments": [
                {
                    "color": self.color,
                    "text": self.text,
                }
            ],
        }
