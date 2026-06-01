from abc import ABC, abstractmethod


class OutreachChannel(ABC):
    """Abstract channel — email, LinkedIn, Instagram DM, SMS all implement this."""

    @abstractmethod
    async def send(self, to: str, subject: str, body: str, from_name: str) -> bool:
        pass

    @abstractmethod
    async def check_replies(self, campaign_id: str) -> list[dict]:
        pass
