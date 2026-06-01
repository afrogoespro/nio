import anthropic
import json
from tavily import TavilyClient
import os


async def research_prospect(
    first_name: str,
    last_name: str,
    company: str | None,
    title: str | None,
    linkedin_url: str | None,
    campaign_context: str,
) -> dict:
    """Find recent, relevant triggers for a prospect to personalize outreach."""

    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    full_name = f"{first_name} {last_name}".strip()

    queries = [f"{full_name} {company or ''} recent news OR post OR interview OR promotion OR event"]
    if linkedin_url:
        queries.append(f"site:linkedin.com {full_name} {company or ''}")

    triggers = []
    for query in queries:
        try:
            results = tavily.search(query=query, max_results=3, search_depth="basic")
            for r in results.get("results", []):
                triggers.append({"title": r.get("title"), "snippet": r.get("content", "")[:300], "url": r.get("url")})
        except Exception:
            pass

    if not triggers:
        return {"triggers": [], "summary": None}

    client = anthropic.AsyncAnthropic()
    prompt = f"""You are researching a prospect for personalized outreach.

Prospect: {full_name}, {title or "unknown title"} at {company or "unknown company"}
Campaign context: {campaign_context}

Web findings:
{json.dumps(triggers, indent=2)}

Identify the single best trigger (recent post, promotion, event, achievement, interest)
that makes the outreach feel personal and relevant. Return JSON:
{{
  "trigger_type": "post|promotion|funding|event|interest|achievement",
  "trigger_summary": "one sentence describing what you found",
  "trigger_source": "url or null",
  "personalization_hook": "how to naturally reference this in an opening line"
}}

If nothing useful found, return {{"trigger_type": null, "trigger_summary": null, "trigger_source": null, "personalization_hook": null}}
Return only valid JSON."""

    message = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    result = json.loads(raw)
    result["raw_triggers"] = triggers
    return result
