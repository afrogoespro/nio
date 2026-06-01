from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from agents.voice_agent import learn_from_edit
from db.session import get_db
from db.queries import (
    get_prospects_for_review,
    approve_prospect_message,
    skip_prospect,
    get_voice_profile,
    update_voice_profile,
)

router = APIRouter(prefix="/review", tags=["review"])


class ApproveMessage(BaseModel):
    campaign_id: str
    prospect_id: str
    subject: str
    body: str
    original_body: str


class RejectMessage(BaseModel):
    campaign_id: str
    prospect_id: str
    reason: str | None = None


@router.get("/queue/{campaign_id}")
async def get_queue(campaign_id: str, db: AsyncSession = Depends(get_db)):
    prospects = await get_prospects_for_review(db, campaign_id)
    return {
        "prospects": [
            {
                "id": str(p.id),
                "first_name": p.first_name,
                "last_name": p.last_name,
                "company": p.company,
                "title": p.title,
                "trigger": p.research.get("trigger_summary") if p.research else None,
                "subject": p.generated_message.get("subject") if p.generated_message else "",
                "body": p.generated_message.get("body") if p.generated_message else "",
            }
            for p in prospects
        ]
    }


@router.post("/approve")
async def approve_message(data: ApproveMessage, db: AsyncSession = Depends(get_db)):
    was_edited = data.body.strip() != data.original_body.strip()

    await approve_prospect_message(db, data.prospect_id, data.subject, data.body)

    if was_edited:
        vp = await get_voice_profile(db, data.campaign_id)
        current = vp.profile if vp else {}
        updated = await learn_from_edit(
            original_message=data.original_body,
            edited_message=data.body,
            current_profile=current,
        )
        await update_voice_profile(db, data.campaign_id, updated)
        return {"queued": True, "learned": True, "updated_voice_profile": updated}

    return {"queued": True, "learned": False, "updated_voice_profile": None}


@router.post("/reject")
async def reject_message(data: RejectMessage, db: AsyncSession = Depends(get_db)):
    await skip_prospect(db, data.prospect_id)

    if data.reason:
        vp = await get_voice_profile(db, data.campaign_id)
        current = vp.profile if vp else {}
        updated = await learn_from_edit(
            original_message="[rejected message]",
            edited_message=f"[user rejected because: {data.reason}]",
            current_profile=current,
        )
        await update_voice_profile(db, data.campaign_id, updated)
        return {"skipped": True, "updated_voice_profile": updated}

    return {"skipped": True, "updated_voice_profile": None}
