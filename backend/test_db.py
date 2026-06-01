"""Quick smoke test for Supabase connection + table creation."""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from db.session import check_connection, create_tables


async def main():
    print("Testing Supabase connection...")
    try:
        await check_connection()
        print("[OK] Connected to Supabase Postgres")
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return

    print("\nCreating tables...")
    try:
        await create_tables()
        print("[OK] Tables created (campaigns, prospects, voice_profiles)")
    except Exception as e:
        print(f"[FAIL] Table creation error: {e}")
        return

    print("\nAll good. Backend is ready to talk to Supabase.")


if __name__ == "__main__":
    asyncio.run(main())
