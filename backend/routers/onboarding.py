from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from agents.icp_agent import derive_icp
from db.session import get_db
from db.queries import create_campaign, set_campaign_icp

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class OnboardingInput(BaseModel):
    user_id: str
    business_description: str
    target_description: str
    goal: str
    tone: str


class OnboardingResponse(BaseModel):
    campaign_id: str
    icp: dict
    message: str


@router.post("/start", response_model=OnboardingResponse)
async def start_campaign(data: OnboardingInput, db: AsyncSession = Depends(get_db)):
    campaign = await create_campaign(db, data.user_id, data.model_dump())

    try:
        icp = await derive_icp(
            business_description=data.business_description,
            target_description=data.target_description,
            goal=data.goal,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ICP derivation failed: {e}")

    await set_campaign_icp(db, str(campaign.id), icp.model_dump())

    return OnboardingResponse(
        campaign_id=str(campaign.id),
        icp=icp.model_dump(),
        message="NIO is set up. I'll start finding and reaching out to people daily.",
    )
