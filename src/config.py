import os


class Config:
    @staticmethod
    def get_central_channel(self) -> str:
        return os.getenv("CENTRAL_CHANNEL")
