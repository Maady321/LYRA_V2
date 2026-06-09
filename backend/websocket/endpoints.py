import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select, update
import json
import asyncio

from backend.websocket.connection_manager import manager
from backend.database.connection import async_session
from backend.models.db_models import Conversation, Message
from backend.services.ollama_service import ollama_service
from backend.core.logger import logger
from backend.security.prompt_firewall_v2 import prompt_firewall
from backend.security.voice_guardian import voice_guardian, VoiceRiskCategory

import sys
import os
import re

# Append MJ_AI_Assistant path so we can import modules from it
current_dir = os.path.dirname(os.path.abspath(__file__))
lyra_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
assistant_dir = os.path.join(lyra_dir, "MJ_AI_Assistant")
if assistant_dir not in sys.path:
    sys.path.append(assistant_dir)

# Initialize MJOrchestrator singleton lazily
mj_orchestrator = None

def get_orchestrator():
    global mj_orchestrator
    if mj_orchestrator is None:
        try:
            from core.orchestrator import MJOrchestrator
            mj_orchestrator = MJOrchestrator()
            logger.info("MJOrchestrator singleton initialized successfully in websocket endpoints.")
        except Exception as e:
            logger.error(f"Failed to initialize MJOrchestrator in endpoints: {e}")
    return mj_orchestrator

router = APIRouter()

async def generate_async_summary(conversation_id: str, first_message: str, model: str):
    """Asynchronously generates a conversation summary title from the first message"""
    logger.info(f"Triggering background title generation for conversation {conversation_id}...")
    try:
        # Wait a short moment to let websocket stream settle
        await asyncio.sleep(0.5)
        
        prompt = (
            f"Generate a short, concise 3 to 5 words title for a conversation starting with this message. "
            f"Respond ONLY with the title itself, no quotation marks, no preamble.\n\n"
            f"Message: {first_message}"
        )
        
        # Call Ollama API directly in a simple request
        import httpx
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 10}
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{ollama_service.api_url}/api/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                title = data.get("message", {}).get("content", "").strip()
                # Clean up quotes if returned
                title = title.replace('"', '').replace("'", "")
                if title:
                    logger.info(f"Generated title: '{title}' for conversation {conversation_id}")
                    # Update in database
                    async with async_session() as db:
                        q = select(Conversation).where(Conversation.id == conversation_id)
                        result = await db.execute(q)
                        conversation = result.scalar_one_or_none()
                        if conversation:
                            conversation.title = title
                            conversation.updated_at = datetime.utcnow()
                            await db.commit()
    except Exception as e:
        logger.error(f"Error generating asynchronous title: {e}")

@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """WebSocket router for streaming chat messages bi-directionally"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Await raw json message from client
            raw_data = await websocket.receive_text()
            try:
                payload = json.loads(raw_data)
            except ValueError:
                await manager.send_json(websocket, {
                    "event": "chat_error",
                    "data": {"message": "Invalid JSON format payload."}
                })
                continue
                
            event = payload.get("event")
            data = payload.get("data", {})
            
            if event != "send_message":
                await manager.send_json(websocket, {
                    "event": "chat_error",
                    "data": {"message": f"Unsupported socket event: '{event}'"}
                })
                continue
                
            # Process user prompt
            conv_id = data.get("conversation_id")
            user_content = data.get("content", "").strip()
            model = data.get("model", "llama3")
            system_prompt = data.get("system_prompt")
            temperature = data.get("temperature")
            max_tokens = data.get("max_tokens")
            context_window = data.get("context_window")
            is_voice = data.get("is_voice", False)
            
            if not conv_id or not user_content:
                await manager.send_json(websocket, {
                    "event": "chat_error",
                    "data": {"message": "Missing conversation_id or message content."}
                })
                continue
                
            # ENTERPRISE PROMPT FIREWALL CHECK
            user_id = "ws_client" # In production, extract from JWT via subprotocol
            is_allowed, firewall_response, audit_data = await prompt_firewall.inspect_prompt(user_id, user_content)
            
            if not is_allowed:
                await manager.send_json(websocket, {
                    "event": "chat_error",
                    "data": {"message": f"Lyra Prompt Firewall Blocked Request: {firewall_response}"}
                })
                continue
            
            user_content = firewall_response # use sanitized prompt
                
            # ENTERPRISE VOICE GUARDIAN CHECK
            if is_voice:
                is_valid, voice_msg = voice_guardian.validate_command(user_content)
                if not is_valid:
                    await manager.send_json(websocket, {
                        "event": "chat_error",
                        "data": {"message": f"Lyra Voice Guardian Blocked Request: {voice_msg}"}
                    })
                    continue
                
            assistant_msg_id = str(uuid.uuid4())
            
            # 1. Establish Db session and insert User & Assistant records
            async with async_session() as db:
                # Confirm conversation session exists
                q = select(Conversation).where(Conversation.id == conv_id)
                res = await db.execute(q)
                conversation = res.scalar_one_or_none()
                
                if not conversation:
                    await manager.send_json(websocket, {
                        "event": "chat_error",
                        "data": {"message": "Active conversation session not found in database.", "conversation_id": conv_id}
                    })
                    continue
                
                # Save User message
                user_msg = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conv_id,
                    role="user",
                    content=user_content,
                    model_used=model,
                    timestamp=datetime.utcnow()
                )
                db.add(user_msg)
                
                # Fetch full chat history in this conversation to pass to Ollama
                hist_query = (
                    select(Message)
                    .where(Message.conversation_id == conv_id)
                    .order_by(Message.timestamp.asc())
                )
                hist_res = await db.execute(hist_query)
                past_messages = hist_res.scalars().all()
                
                # Convert standard history to Ollama parameters
                ollama_messages = [
                    {"role": m.role, "content": m.content}
                    for m in past_messages
                ]
                # Append current user prompt
                ollama_messages.append({"role": "user", "content": user_content})
                
                # Save initial Assistant message record (empty text, to be populated)
                assistant_msg = Message(
                    id=assistant_msg_id,
                    conversation_id=conv_id,
                    role="assistant",
                    content="",
                    model_used=model,
                    timestamp=datetime.utcnow()
                )
                db.add(assistant_msg)
                
                # Update conversation updated timestamp
                conversation.updated_at = datetime.utcnow()
                await db.commit()
                
                # Check if we should trigger title summary generation
                should_summarize = (conversation.title == "New Conversation" or conversation.title == "")

            # Check if this user prompt is an automation/task command
            from backend.tools.task_manager import task_manager
            task_response = task_manager.execute_task(user_content)

            if task_response:
                # Tell client we are starting the generation stream
                await manager.send_json(websocket, {
                    "event": "chat_start",
                    "data": {
                        "conversation_id": conv_id,
                        "message_id": assistant_msg_id,
                        "model": model
                    }
                })

                # Stream the task execution response token-by-token for beautiful styling
                words = task_response.split(" ")
                for idx, word in enumerate(words):
                    token = word + (" " if idx < len(words) - 1 else "")
                    await manager.send_json(websocket, {
                        "event": "chat_token",
                        "data": {
                            "token": token,
                            "message_id": assistant_msg_id
                        }
                    })
                    await asyncio.sleep(0.015)

                # Save execution reply to database
                async with async_session() as db:
                    q = select(Message).where(Message.id == assistant_msg_id)
                    res = await db.execute(q)
                    db_msg = res.scalar_one_or_none()
                    if db_msg:
                        db_msg.content = task_response
                        await db.commit()

                # Tell client the stream is complete
                await manager.send_json(websocket, {
                    "event": "chat_end",
                    "data": {
                        "message_id": assistant_msg_id,
                        "conversation_id": conv_id,
                        "full_content": task_response,
                        "metrics": {
                            "prompt_eval_count": 0,
                            "eval_count": len(words),
                            "total_duration": 100000000
                        }
                    }
                })

                # Asynchronously trigger title generation in the background if first message
                if should_summarize:
                    asyncio.create_task(
                        generate_async_summary(conv_id, user_content, model)
                    )

                # Bypass standard Ollama generation block
                continue

            # 2. Tell client we are starting the generation stream
            await manager.send_json(websocket, {
                "event": "chat_start",
                "data": {
                    "conversation_id": conv_id,
                    "message_id": assistant_msg_id,
                    "model": model
                }
            })
            
            # 3. Stream from agents and pipe back to WebSocket
            full_assistant_reply = ""
            metrics = {}
            stream_failed = False
            
            log_queue = asyncio.Queue()
            loop = asyncio.get_running_loop()
            
            async def log_streamer():
                try:
                    while True:
                        event = await log_queue.get()
                        log_data = event.data
                        log_text = log_data.get("log", "")
                        sender = event.sender
                        
                        # Beautiful telemetry logs
                        formatted_log = f"\n🤖 **[{sender}]** *{log_text}*\n"
                        
                        await manager.send_json(websocket, {
                            "event": "chat_token",
                            "data": {
                                "token": formatted_log,
                                "message_id": assistant_msg_id
                            }
                        })
                        log_queue.task_done()
                except asyncio.CancelledError:
                    pass
                except Exception as ex:
                    logger.error(f"Error in log_streamer: {ex}")
                    
            def log_callback(event):
                loop.call_soon_threadsafe(log_queue.put_nowait, event)
                
            orchestrator = get_orchestrator()
            if orchestrator:
                try:
                    orchestrator.db.create_conversation(conv_id, "Lyra UI Session")
                except Exception as sync_err:
                    logger.error(f"Failed to sync conversation session to agent database: {sync_err}")
                orchestrator.bus.subscribe("system_monitor_channel", log_callback)
                
            streamer_task = asyncio.create_task(log_streamer())
            
            try:
                if orchestrator:
                    final_answer = await orchestrator.execute_query(user_content, conv_id)
                else:
                    logger.warning("MJOrchestrator not available, falling back to direct Ollama streaming.")
                    final_chunks = []
                    async for chunk in ollama_service.stream_chat(
                        model=model,
                        messages=ollama_messages,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        context_window=context_window
                    ):
                        event_type = chunk.get("event")
                        if event_type == "error":
                            raise Exception(chunk.get("message"))
                        elif event_type == "token":
                            final_chunks.append(chunk.get("token", ""))
                    final_answer = "".join(final_chunks)
            except Exception as stream_ex:
                logger.error(f"Error executing agent workflow: {stream_ex}")
                stream_failed = True
                await manager.send_json(websocket, {
                    "event": "chat_error",
                    "data": {"message": f"Agent Execution Interruption: {str(stream_ex)}", "conversation_id": conv_id}
                })
            finally:
                if orchestrator and "system_monitor_channel" in orchestrator.bus._listeners:
                    if log_callback in orchestrator.bus._listeners["system_monitor_channel"]:
                        orchestrator.bus._listeners["system_monitor_channel"].remove(log_callback)
                streamer_task.cancel()
                try:
                    await streamer_task
                except asyncio.CancelledError:
                    pass
                    
            # 4. Stream synthesized result token-by-token and save to database
            if not stream_failed:
                # Add separator between telemetry logs and final answer
                await manager.send_json(websocket, {
                    "event": "chat_token",
                    "data": {
                        "token": "\n\n---\n\n",
                        "message_id": assistant_msg_id
                    }
                })
                
                # Split and stream
                tokens = re.split(r'(\s+)', final_answer)
                for token in tokens:
                    if not token:
                        continue
                    full_assistant_reply += token
                    await manager.send_json(websocket, {
                        "event": "chat_token",
                        "data": {
                            "token": token,
                            "message_id": assistant_msg_id
                        }
                    })
                    await asyncio.sleep(0.008)
                    
                metrics = {
                    "prompt_eval_count": 0,
                    "eval_count": len(tokens),
                    "total_duration": 100000000
                }
                
                async with async_session() as db:
                    q = select(Message).where(Message.id == assistant_msg_id)
                    res = await db.execute(q)
                    db_msg = res.scalar_one_or_none()
                    
                    if db_msg:
                        db_msg.content = full_assistant_reply
                        db_msg.prompt_tokens = metrics.get("prompt_eval_count")
                        db_msg.completion_tokens = metrics.get("eval_count")
                        db_msg.total_duration = metrics.get("total_duration")
                        
                        conv_q = select(Conversation).where(Conversation.id == conv_id)
                        conv_res = await db.execute(conv_q)
                        db_conv = conv_res.scalar_one_or_none()
                        if db_conv:
                            db_conv.updated_at = datetime.utcnow()
                            
                        await db.commit()
                        
                await manager.send_json(websocket, {
                    "event": "chat_end",
                    "data": {
                        "message_id": assistant_msg_id,
                        "conversation_id": conv_id,
                        "full_content": full_assistant_reply,
                        "metrics": metrics
                    }
                })
                
                if should_summarize:
                    asyncio.create_task(
                        generate_async_summary(conv_id, user_content, model)
                    )
            else:
                async with async_session() as db:
                    q = select(Message).where(Message.id == assistant_msg_id)
                    res = await db.execute(q)
                    db_msg = res.scalar_one_or_none()
                    if db_msg:
                        await db.delete(db_msg)
                        await db.commit()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected gracefully.")
    except Exception as e:
        manager.disconnect(websocket)
        logger.error(f"WebSocket master handler exception: {e}")
