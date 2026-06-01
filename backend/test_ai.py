"""Smoke test: verify Anthropic key works through one of the agents."""
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

from agents.icp_agent import derive_icp


async def main():
    print("Testing Anthropic API via icp_agent.derive_icp...")
    try:
        icp = await derive_icp(
            business_description="A boutique branding studio for early-stage SaaS startups.",
            target_description="Founders of seed-stage B2B SaaS companies preparing for Series A.",
            goal="Book 30-min intro calls with qualified founders.",
        )
        print("[OK] ICP derived:")
        print(f"  Job titles: {icp.job_titles[:3]}...")
        print(f"  Industries: {icp.industries[:3]}...")
        print(f"  Reasoning: {icp.reasoning}")
    except Exception as e:
        print(f"[FAIL] {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
