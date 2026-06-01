from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import os

# Railway injects DATABASE_URL as postgres:// — we need postgresql+asyncpg://
_raw = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/nio")
DATABASE_URL = _raw.replace("postgres://", "postgresql+asyncpg://", 1)

# Use NullPool when going through Supabase's pgbouncer-based pooler so we don't
# double-pool connections (which causes refused-connection issues).
_engine_kwargs = {"echo": False}
if "pooler.supabase.com" in DATABASE_URL:
    _engine_kwargs["poolclass"] = NullPool
    _engine_kwargs["connect_args"] = {"statement_cache_size": 0}

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    from models.campaign import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_connection():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
