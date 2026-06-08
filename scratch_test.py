import asyncio
import os
import sys

# Setup paths so we can import backend packages
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.ollama_service import ollama_service

async def test_stream():
    print("Testing streaming chat with llama3:8b...")
    messages = [{"role": "user", "content": "tell me about apple fruit in 5 words"}]
    
    try:
        async for chunk in ollama_service.stream_chat(
            model="llama3:8b",
            messages=messages,
            system_prompt="You are a helpful assistant.",
            temperature=0.7
        ):
            print("YIELDED CHUNK:", chunk)
    except Exception as e:
        print("EXCEPTION RAISED:", e)

if __name__ == "__main__":
    asyncio.run(test_stream())
