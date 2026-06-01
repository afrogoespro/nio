import anthropic
import json


async def generate_message(
    first_name: str,
    company: str | None,
    title: str | None,
    business_description: str,
    goal: str,
    tone: str,
    research: dict,
    voice_profile: dict | None = None,
) -> dict:
    client = anthropic.AsyncAnthropic()

    trigger = research.get("personalization_hook") or ""
    trigger_summary = research.get("trigger_summary") or ""

    voice_instructions = ""
    if voice_profile:
        voice_instructions = f"""
VOICE PROFILE (write exactly like this person talks):
- Energy: {voice_profile.get('energy')}
- Formality: {voice_profile.get('formality')}
- Sentence length: {voice_profile.get('sentence_length')}
- Vocabulary: {voice_profile.get('vocabulary_level')} — everyday words only
- Their vibe: {voice_profile.get('overall_vibe')}
- Phrases they use: {', '.join(voice_profile.get('characteristic_phrases', []))}
- Words to NEVER use: {', '.join(voice_profile.get('words_they_avoid', []))}
- Example of their voice: "{voice_profile.get('example_opener')}"
"""

    prompt = f"""Write a cold outreach email that sounds like a real human wrote it — not marketing copy.

About the sender: {business_description}
Goal: {goal}
Tone: {tone}
{voice_instructions}

Prospect: {first_name}, {title or ''} at {company or 'their company'}
Personal hook: {trigger_summary}
How to use it: {trigger}

Rules:
- Sound like a real person texting, not a marketer emailing
- NO words like: leverage, synergy, reach out, touch base, circle back, utilize, innovative, solutions
- Short sentences. Simple words. A 16 year old should get it immediately.
- 3-5 sentences max. No fluff opener.
- If there's a personal hook, use it naturally in the first line — not forced
- End with one soft question, not a calendar link
- Subject line: casual, lowercase, like you'd write to a friend

Return JSON:
{{
  "subject": "subject line",
  "body": "email body"
}}

Return only valid JSON."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(message.content[0].text.strip())
