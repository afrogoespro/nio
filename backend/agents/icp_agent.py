import anthropic
import json
from pydantic import BaseModel


class ICP(BaseModel):
    job_titles: list[str]
    industries: list[str]
    company_size_min: int | None
    company_size_max: int | None
    locations: list[str]
    keywords: list[str]
    seniority_levels: list[str]
    reasoning: str


async def derive_icp(
    business_description: str,
    target_description: str,
    goal: str,
) -> ICP:
    client = anthropic.AsyncAnthropic()

    prompt = f"""You are an expert B2B/B2C sales strategist. Based on the business and target info below,
derive a precise Ideal Customer Profile (ICP) that can be used to search Apollo.io for prospects.

Business: {business_description}
Target audience: {target_description}
Goal of outreach: {goal}

Return a JSON object with these fields:
- job_titles: list of relevant job titles to target (be specific, e.g. "Music Director" not just "Manager")
- industries: list of relevant industries
- company_size_min: minimum company headcount (null if not relevant)
- company_size_max: maximum company headcount (null if not relevant)
- locations: list of cities/regions to target (empty if nationwide)
- keywords: list of keywords that describe the ideal prospect
- seniority_levels: e.g. ["entry", "manager", "director"]
- reasoning: one sentence explaining why this ICP fits the goal

Return only valid JSON, no markdown."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    data = json.loads(raw)
    return ICP(**data)
