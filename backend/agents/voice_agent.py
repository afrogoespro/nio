import anthropic
import json


TRAINING_QUESTIONS = [
    "how would you describe what you do to someone you just met at a bar?",
    "if a friend asked why they should check out your business, what would you say?",
    "how do you usually start a conversation with someone new?",
]


async def chat_training(
    conversation_history: list[dict],
    user_message: str,
) -> dict:
    """
    Conversational voice training. Asks the user casual questions,
    listens to how they naturally write/talk.
    Returns the AI reply + whether training is complete.
    """
    client = anthropic.AsyncAnthropic()

    system = """You are helping someone teach you how they naturally talk so you can write outreach that sounds like them.

Ask them casual, friendly questions one at a time. Keep it conversational, like texting a friend.
You want to learn:
- how formal or casual they are
- how long their sentences are
- words they use vs words they'd never use
- their energy level (hyped, chill, dry, etc.)
- any slang or phrases they repeat

After 3-4 exchanges where you have enough examples, respond with a JSON block at the end of your message like:
<voice_ready>true</voice_ready>

Until then, just chat naturally. Ask one question at a time. Keep your replies short."""

    messages = conversation_history + [{"role": "user", "content": user_message}]

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system,
        messages=messages,
    )

    reply = response.content[0].text
    ready = "<voice_ready>true</voice_ready>" in reply
    clean_reply = reply.replace("<voice_ready>true</voice_ready>", "").strip()

    return {
        "reply": clean_reply,
        "training_complete": ready,
        "updated_history": messages + [{"role": "assistant", "content": reply}],
    }


async def extract_voice_profile(conversation_history: list[dict]) -> dict:
    """
    After training chat, extract a concise voice profile from the conversation.
    """
    client = anthropic.AsyncAnthropic()

    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in conversation_history
        if m["role"] == "user"
    )

    prompt = f"""Based on how this person writes in the conversation below, build a voice profile.

Their messages:
{transcript}

Return JSON:
{{
  "energy": "chill|warm|hyped|dry|enthusiastic",
  "formality": "very_casual|casual|neutral",
  "sentence_length": "short|medium|varies",
  "vocabulary_level": "simple|everyday|mixed",
  "characteristic_phrases": ["list of phrases or words they used that feel like them"],
  "words_they_avoid": ["formal or corporate words they clearly don't use"],
  "overall_vibe": "one sentence describing how they come across",
  "example_opener": "write a sample opening line in their exact voice for a cold outreach"
}}

Return only valid JSON."""

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(message.content[0].text.strip())


async def learn_from_edit(
    original_message: str,
    edited_message: str,
    current_profile: dict,
) -> dict:
    """
    When a user edits a generated message, update the voice profile to reflect what they changed.
    """
    client = anthropic.AsyncAnthropic()

    prompt = f"""Someone edited an AI-generated outreach message. Learn from the diff to improve their voice profile.

Original (AI wrote):
{original_message}

Edited (what they actually want):
{edited_message}

Current voice profile:
{json.dumps(current_profile, indent=2)}

What changed and what does it tell you about their voice?
Update the profile to reflect what you learned. Return the full updated profile JSON.
Return only valid JSON."""

    message = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return json.loads(message.content[0].text.strip())
