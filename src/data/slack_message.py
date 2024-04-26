from dataclasses import dataclass
from typing import Any, Dict, List
import json

from src.data.notification import Notification


@dataclass
class SlackMessage(Notification):
    channels: List[str]
    header: str
    title: str
    text: str
    color: str

    def __init__(self, channels: List[str], header: str, title: str, text: str, color: str):
        self.channels = list(filter(None, channels))
        self.header = header
        self.title = title
        self.text = text
        self.color = color

    @staticmethod
    def text_to_blocks(report_text):
        block_section = json.dumps({"type": "section", "text": {"type": "mrkdwn", "text": report_text}})
        return block_section

    def to_dict(self) -> Dict[str, Any]:
        return {
            "channelLookup": {
                "by": "slack-channel",
                "slackChannels": self.channels,
            },
            "displayName": self.title,
            "emoji": ":this-is-fine:",
            "blocks": [
                self.header,
                SlackMessage.text_to_blocks(self.text),
            ],
            "attachments": [
                {
                    "color": self.color,
                    "title": self.title,
                    "text": self.text,
                }
            ],
        }


# "blocks": [
#     self.header,
#     # SlackMessage.text_to_blocks(self.text),
# ],
