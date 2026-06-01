from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
import uuid

from models.campaign import Campaign, CampaignStatus
from models.prospect import Prospect, ProspectStatus
from models.voice_profile import VoiceProfile


# ── campaigns ──────────────────────────────────────────────

async def create_campaign(db: AsyncSession, user_id: str, data: dict) -> Campaign:
    campaign = Campaign(
        id=uuid.uuid4(),
        user_id=user_id,
        business_description=data["business_description"],
        target_description=data["target_description"],
        goal=data["goal"],
        tone=data["tone"],
        status=CampaignStatus.onboarding,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def get_campaign(db: AsyncSession, campaign_id: str) -> Campaign | None:
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    return result.scalar_one_or_none()


async def set_campaign_icp(db: AsyncSession, campaign_id: str, icp: dict) -> None:
    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(icp=icp, status=CampaignStatus.active)
    )
    await db.commit()


async def get_active_campaigns(db: AsyncSession) -> list[Campaign]:
    result = await db.execute(select(Campaign).where(Campaign.status == CampaignStatus.active))
    return list(result.scalars().all())


# ── prospects ──────────────────────────────────────────────

async def save_prospect(db: AsyncSession, campaign_id: str, data: dict, research: dict, message: dict) -> Prospect:
    prospect = Prospect(
        id=uuid.uuid4(),
        campaign_id=campaign_id,
        first_name=data["first_name"],
        last_name=data.get("last_name"),
        email=data["email"],
        company=data.get("company"),
        title=data.get("title"),
        linkedin_url=data.get("linkedin_url"),
        apollo_id=data.get("apollo_id"),
        research=research,
        generated_message=message,
        status=ProspectStatus.message_ready,
    )
    db.add(prospect)
    await db.commit()
    await db.refresh(prospect)
    return prospect


async def get_prospects_for_review(db: AsyncSession, campaign_id: str) -> list[Prospect]:
    result = await db.execute(
        select(Prospect)
        .where(Prospect.campaign_id == campaign_id)
        .where(Prospect.status == ProspectStatus.message_ready)
    )
    return list(result.scalars().all())


async def mark_prospect_sent(db: AsyncSession, prospect_id: str) -> None:
    await db.execute(
        update(Prospect)
        .where(Prospect.id == prospect_id)
        .values(status=ProspectStatus.sent, sent_at=datetime.now(timezone.utc))
    )
    await db.commit()


async def mark_prospect_replied(db: AsyncSession, prospect_id: str) -> None:
    await db.execute(
        update(Prospect)
        .where(Prospect.id == prospect_id)
        .values(status=ProspectStatus.replied, replied_at=datetime.now(timezone.utc))
    )
    await db.commit()


async def get_sent_emails(db: AsyncSession, campaign_id: str) -> set[str]:
    result = await db.execute(
        select(Prospect.email)
        .where(Prospect.campaign_id == campaign_id)
        .where(Prospect.status.in_([ProspectStatus.sent, ProspectStatus.replied]))
    )
    return {row[0] for row in result.fetchall()}


async def approve_prospect_message(db: AsyncSession, prospect_id: str, subject: str, body: str) -> None:
    await db.execute(
        update(Prospect)
        .where(Prospect.id == prospect_id)
        .values(generated_message={"subject": subject, "body": body}, status=ProspectStatus.queued)
    )
    await db.commit()


async def skip_prospect(db: AsyncSession, prospect_id: str) -> None:
    await db.execute(
        update(Prospect)
        .where(Prospect.id == prospect_id)
        .values(status=ProspectStatus.unsubscribed)
    )
    await db.commit()


# ── voice profile ──────────────────────────────────────────

async def save_voice_profile(db: AsyncSession, campaign_id: str, profile: dict, history: list) -> VoiceProfile:
    existing = await get_voice_profile(db, campaign_id)
    if existing:
        await db.execute(
            update(VoiceProfile)
            .where(VoiceProfile.campaign_id == campaign_id)
            .values(profile=profile, training_history=history, updated_at=datetime.now(timezone.utc))
        )
        await db.commit()
        return existing

    vp = VoiceProfile(
        id=uuid.uuid4(),
        campaign_id=campaign_id,
        profile=profile,
        training_history=history,
    )
    db.add(vp)
    await db.commit()
    await db.refresh(vp)
    return vp


async def get_voice_profile(db: AsyncSession, campaign_id: str) -> VoiceProfile | None:
    result = await db.execute(
        select(VoiceProfile).where(VoiceProfile.campaign_id == campaign_id)
    )
    return result.scalar_one_or_none()


async def update_voice_profile(db: AsyncSession, campaign_id: str, profile: dict) -> None:
    await db.execute(
        update(VoiceProfile)
        .where(VoiceProfile.campaign_id == campaign_id)
        .values(profile=profile, updated_at=datetime.now(timezone.utc))
    )
    await db.commit()


# ── campaign controls ─────────────────────────────────────

async def pause_campaign(db: AsyncSession, campaign_id: str) -> None:
    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status=CampaignStatus.paused)
    )
    await db.commit()


async def resume_campaign(db: AsyncSession, campaign_id: str) -> None:
    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status=CampaignStatus.active)
    )
    await db.commit()


async def update_campaign_last_run(db: AsyncSession, campaign_id: str) -> None:
    await db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(last_run_at=datetime.now(timezone.utc))
    )
    await db.commit()


# ── dashboard stats ───────────────────────────────────────

async def get_campaign_stats(db: AsyncSession, campaign_id: str) -> dict:
    from sqlalchemy import func, case, cast, Date

    today = datetime.now(timezone.utc).date()

    result = await db.execute(
        select(
            func.count().label("total"),
            func.count(case((Prospect.status == ProspectStatus.sent, 1))).label("sent"),
            func.count(case((Prospect.status == ProspectStatus.replied, 1))).label("replied"),
            func.count(case((Prospect.status == ProspectStatus.lead, 1))).label("leads"),
            func.count(case((Prospect.status == ProspectStatus.message_ready, 1))).label("pending_review"),
            func.count(case((Prospect.status == ProspectStatus.queued, 1))).label("queued"),
            func.count(case((
                (Prospect.sent_at != None) & (cast(Prospect.sent_at, Date) == today), 1
            ))).label("sent_today"),
        )
        .where(Prospect.campaign_id == campaign_id)
    )
    row = result.one()
    return {
        "total_prospects": row.total,
        "sent": row.sent,
        "sent_today": row.sent_today,
        "replied": row.replied,
        "leads": row.leads,
        "pending_review": row.pending_review,
        "queued": row.queued,
    }


async def get_recent_activity(db: AsyncSession, campaign_id: str, limit: int = 20) -> list[dict]:
    result = await db.execute(
        select(Prospect)
        .where(Prospect.campaign_id == campaign_id)
        .order_by(Prospect.created_at.desc())
        .limit(limit)
    )
    prospects = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "first_name": p.first_name,
            "last_name": p.last_name,
            "company": p.company,
            "status": p.status.value,
            "trigger": p.research.get("trigger_summary") if p.research else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "sent_at": p.sent_at.isoformat() if p.sent_at else None,
        }
        for p in prospects
    ]
