import asyncio
import random
import json
import os
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from agents.research_agent import research_prospect
from agents.copy_agent import generate_message
from channels.email import EmailChannel
from integrations.apollo import find_prospects
from db.queries import (
    get_campaign,
    get_sent_emails,
    save_prospect,
    mark_prospect_sent,
    get_voice_profile,
    update_campaign_last_run,
)


SENDS_PER_HOUR = 4
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")

_running_campaigns: set[str] = set()


def is_campaign_running(campaign_id: str) -> bool:
    return campaign_id in _running_campaigns


async def run_campaign(campaign_id: str, db: AsyncSession) -> dict:
    """Main autopilot loop for a single campaign. Returns a summary dict."""

    if campaign_id in _running_campaigns:
        return {"error": "Campaign is already running"}

    campaign = await get_campaign(db, campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    icp = campaign.icp
    if not icp:
        return {"error": "No ICP configured — complete onboarding first"}

    _running_campaigns.add(campaign_id)
    try:
        raw_prospects = await find_prospects(icp, limit=30)

        existing_emails = await get_sent_emails(db, campaign_id)
        new_prospects = [p for p in raw_prospects if p["email"] not in existing_emails]

        vp = await get_voice_profile(db, campaign_id)
        voice_profile = vp.profile if vp else None

        channel = EmailChannel()
        sent_count = 0
        daily_cap = SENDS_PER_HOUR * 8

        for prospect in new_prospects:
            if sent_count >= daily_cap:
                break

            research = await research_prospect(
                first_name=prospect["first_name"],
                last_name=prospect["last_name"],
                company=prospect.get("company"),
                title=prospect.get("title"),
                linkedin_url=prospect.get("linkedin_url"),
                campaign_context=campaign.business_description,
            )

            message = await generate_message(
                first_name=prospect["first_name"],
                company=prospect.get("company"),
                title=prospect.get("title"),
                business_description=campaign.business_description,
                goal=campaign.goal,
                tone=campaign.tone,
                research=research,
                voice_profile=voice_profile,
            )

            saved = await save_prospect(db, campaign_id, prospect, research, message)

            success = await channel.send(
                to=prospect["email"],
                subject=message["subject"],
                body=message["body"],
                from_name=campaign.user_id,
            )

            if success:
                await mark_prospect_sent(db, str(saved.id))
                sent_count += 1

            delay = random.uniform(480, 1200)
            await asyncio.sleep(delay)

        await update_campaign_last_run(db, campaign_id)

        summary = {
            "campaign_id": campaign_id,
            "prospects_found": len(raw_prospects),
            "new_prospects": len(new_prospects),
            "sent": sent_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(f"[NIO] {summary}")
        return summary

    finally:
        _running_campaigns.discard(campaign_id)


async def notify_lead(prospect: dict, campaign: dict) -> None:
    channel = EmailChannel()
    await channel.send(
        to=NOTIFICATION_EMAIL,
        subject=f"New lead: {prospect['first_name']} {prospect.get('last_name', '')} replied!",
        body=f"{prospect['first_name']} at {prospect.get('company', 'unknown')} replied to your outreach.\n\nReply to: {prospect['email']}",
        from_name="NIO",
    )
