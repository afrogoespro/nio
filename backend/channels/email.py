import resend
import os
from .base import OutreachChannel


class EmailChannel(OutreachChannel):

    def __init__(self):
        resend.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "outreach@yourdomain.com")

    async def send(self, to: str, subject: str, body: str, from_name: str) -> bool:
        try:
            resend.Emails.send({
                "from": f"{from_name} <{self.from_email}>",
                "to": [to],
                "subject": subject,
                "text": body,
            })
            return True
        except Exception as e:
            print(f"Email send failed to {to}: {e}")
            return False

    async def check_replies(self, campaign_id: str) -> list[dict]:
        # Resend webhooks handle inbound replies — placeholder for now
        return []
