import sys
import os
import asyncio

sys.path.append("MJ_AI_Assistant")
from core.orchestrator import MJOrchestrator

async def test():
    print("Initializing MJOrchestrator...")
    orchestrator = MJOrchestrator()
    print("Executing query...")
    # Mock embeddings to run offline without Ollama embed model lookup issues
    orchestrator.client.generate_embedding = lambda text, *args, **kwargs: [0.1] * 768
    
    # Check if FURY is registered on bus
    print("Registered agents:", list(orchestrator.bus._agent_task_handlers.keys()))
    
    response = await orchestrator.execute_query("Hello Fury, tell me what you can do.", "test_conv_id")
    print("\n--- Response ---")
    print(response)
    print("----------------")

if __name__ == "__main__":
    asyncio.run(test())
