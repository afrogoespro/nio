import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db, AsyncSessionLocal
from db.queries import (
    get_campaign,
    get_campaign_stats,
    get_recent_activity,
    pause_campaign,
    resume_campaign,
)
from scheduler.daily_runner import run_campaign, is_campaign_running

router = APIRouter(prefix="/campaign", tags=["campaign"])


async def _run_in_background(campaign_id: str):
    async with AsyncSessionLocal() as db:
        await run_campaign(campaign_id, db)


@router.post("/{campaign_id}/run")
async def trigger_run(campaign_id: str, background_tasks: BackgroundTasks):
    if is_campaign_running(campaign_id):
        return {"status": "already_running"}

    background_tasks.add_task(_run_in_background, campaign_id)
    return {"status": "started"}


@router.get("/{campaign_id}/stats")
async def campaign_stats(campaign_id: str, db: AsyncSession = Depends(get_db)):
    campaign = await get_campaign(db, campaign_id)
    if not campaign:
        return {"error": "Campaign not found"}

    stats = await get_campaign_stats(db, campaign_id)
    return {
        "campaign_id": str(campaign.id),
        "status": campaign.status.value,
        "last_run_at": campaign.last_run_at.isoformat() if campaign.last_run_at else None,
        "running": is_campaign_running(campaign_id),
        **stats,
    }


@router.get("/{campaign_id}/activity")
async def campaign_activity(campaign_id: str, db: AsyncSession = Depends(get_db)):
    activity = await get_recent_activity(db, campaign_id)
    return {"activity": activity}


@router.post("/{campaign_id}/pause")
async def pause(campaign_id: str, db: AsyncSession = Depends(get_db)):
    await pause_campaign(db, campaign_id)
    return {"status": "paused"}


@router.post("/{campaign_id}/resume")
async def resume(campaign_id: str, db: AsyncSession = Depends(get_db)):
    await resume_campaign(db, campaign_id)
    return {"status": "active"}
