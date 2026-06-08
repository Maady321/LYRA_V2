import sys
import os
import asyncio
import json
import websockets

async def test_chat():
    uri = "ws://127.0.0.1:8000/api/ws/chat"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket.")
        
        # We need a conversation ID. Let's create a mockup one
        conv_id = "test_conversation_agentic_001"
        
        # First, let's create the conversation session in lyra.db via HTTP POST
        import httpx
        try:
            res = httpx.post("http://127.0.0.1:8000/api/conversations", json={"title": "Test Agent Integration"})
            if res.status_code == 201:
                conv_id = res.json()["id"]
                print(f"Created conversation session {conv_id} in lyra.db")
        except Exception as e:
            print(f"Failed to create conversation via REST API: {e}")
            
        payload = {
            "event": "send_message",
            "data": {
                "conversation_id": conv_id,
                "content": "Check my computer health status please.",
                "model": "qwen2.5:1.5b"
            }
        }
        
        await websocket.send(json.dumps(payload))
        print("Sent prompt. Awaiting stream...\n")
        
        try:
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                event = data.get("event")
                event_data = data.get("data", {})
                
                if event == "chat_start":
                    print(f"[START] msg_id: {event_data.get('message_id')}\n")
                elif event == "chat_token":
                    token = event_data.get("token", "")
                    sys.stdout.write(token)
                    sys.stdout.flush()
                elif event == "chat_end":
                    print(f"\n[END] Full response completed.")
                    break
                elif event == "chat_error":
                    print(f"\n[ERROR] {event_data.get('message')}")
                    break
        except Exception as e:
            print(f"\nException during stream: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
