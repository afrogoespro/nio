from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from agents.voice_agent import chat_training, extract_voice_profile, learn_from_edit
from db.session import get_db
from db.queries import save_voice_profile, get_voice_profile, update_voice_profile

router = APIRouter(prefix="/voice", tags=["voice"])


class ChatMessage(BaseModel):
    campaign_id: str
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    training_complete: bool
    history: list[dict]
    voice_profile: dict | None = None


class EditFeedback(BaseModel):
    campaign_id: str
    original: str
    edited: str


@router.post("/chat", response_model=ChatResponse)
async def voice_chat(data: ChatMessage, db: AsyncSession = Depends(get_db)):
    result = await chat_training(
        conversation_history=data.history,
        user_message=data.message,
    )

    voice_profile = None
    if result["training_complete"]:
        voice_profile = await extract_voice_profile(result["updated_history"])
        await save_voice_profile(db, data.campaign_id, voice_profile, result["updated_history"])

    return ChatResponse(
        reply=result["reply"],
        training_complete=result["training_complete"],
        history=result["updated_history"],
        voice_profile=voice_profile,
    )


@router.get("/{campaign_id}")
async def get_profile(campaign_id: str, db: AsyncSession = Depends(get_db)):
    vp = await get_voice_profile(db, campaign_id)
    if not vp:
        return {"voice_profile": None}
    return {"voice_profile": vp.profile}


@router.post("/learn")
async def learn_from_user_edit(data: EditFeedback, db: AsyncSession = Depends(get_db)):
    vp = await get_voice_profile(db, data.campaign_id)
    current = vp.profile if vp else {}

    updated = await learn_from_edit(
        original_message=data.original,
        edited_message=data.edited,
        current_profile=current,
    )
    await update_voice_profile(db, data.campaign_id, updated)
    return {"voice_profile": updated}
