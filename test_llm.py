# test_llm.py
import asyncio
from utils import call_llm

async def test():
    reply = await call_llm([{"role": "user", "content": "Say hello"}])
    print("AI Reply:", reply)

asyncio.run(test())