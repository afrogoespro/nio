from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db.session import create_tables, AsyncSessionLocal
from db.queries import get_active_campaigns
from scheduler.daily_runner import run_campaign
from routers.onboarding import router as onboarding_router
from routers.voice import router as voice_router
from routers.review import router as review_router
from routers.campaign import router as campaign_router

load_dotenv(override=True)

scheduler = AsyncIOScheduler()


async def scheduled_run():
    """Runs all active campaigns. Called by APScheduler on the configured interval."""
    async with AsyncSessionLocal() as db:
        campaigns = await get_active_campaigns(db)

    for campaign in campaigns:
        async with AsyncSessionLocal() as db:
            await run_campaign(str(campaign.id), db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tables are managed via Supabase migrations, not auto-created here
    scheduler.add_job(scheduled_run, "cron", hour=9, minute=0, id="daily_outreach")
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="NIO — Natural Intelligent Outreach", version="0.1.0", lifespan=lifespan)

import os

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in ALLOWED_ORIGINS if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding_router)
app.include_router(voice_router)
app.include_router(review_router)
app.include_router(campaign_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": "nio"}
