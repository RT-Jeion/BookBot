# utils.py
import aiohttp
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# SALESPERSON PROMPT — Friendly, Persuasive, Step-by-Step
SYSTEM_PROMPT = """
You are **BookBot**, a friendly and professional online book salesperson on a Facebook bookstore.

Your job:
1. Greet warmly and build rapport.
2. Ask what kind of book the customer wants (genre, author, title).
3. Recommend 1–3 books with price and short pitch.
4. Ask: "Would you like to buy [Book Name] for [Price]?"
5. After confirmation → Ask: "Great! What's your full name, phone number, and delivery address?"
6. Confirm: "Order confirmed! Total: [Price]. Tracking: [TRK-XXX]"

Rules:
- Be warm, friendly, and persuasive.
- NEVER speak Bangla.
- Keep replies short (2–3 lines max).
- Always push toward purchase.
- Use *bold* for book titles and prices.
"""

# === ASYNC LLM CALL (FREE & WORKING) ===
async def call_llm(messages: List[Dict], temperature=0.3, max_tokens=200) -> str:
    if not messages:
        messages = [{"role": "user", "content": "Hi"}]

    payload = {
        "model": "anthropic/claude-sonnet-4.5",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages[-7:],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                timeout=15
            ) as resp:
                text = await resp.text()
                if resp.status == 401:
                    return "Invalid API key. Get a new one from openrouter.ai/keys"
                if resp.status != 200:
                    return f"AI error {resp.status}. Try again."
                data = await resp.json()
                content = data["choices"][0]["message"]["content"].strip()
                return content if content else "AI returned nothing."
    except Exception as e:
        logger.error(f"LLM Error: {e}")

        return "AI down. Try again."
