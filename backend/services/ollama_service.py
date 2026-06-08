import json
from typing import AsyncGenerator, Dict, List, Any, Optional
import httpx
from backend.core.config import settings
from backend.core.logger import logger
from backend.models.db_models import ModelInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class OllamaService:
    def __init__(self):
        self.api_url = settings.OLLAMA_API_URL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def is_ollama_running(self) -> bool:
        """Check if local Ollama daemon is active and responding"""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.api_url}/")
                return response.status_code == 200 and "Ollama is running" in response.text
        except Exception:
            return False

    async def fetch_and_sync_models(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Fetch installed models from Ollama daemon, and sync into SQLite database"""
        is_running = await self.is_ollama_running()
        if not is_running:
            logger.warning("Ollama is not running. Unable to sync models.")
            # Return currently cached models in database
            result = await db.execute(select(ModelInfo))
            cached = result.scalars().all()
            return [
                {
                    "name": m.name,
                    "parameter_size": m.parameter_size,
                    "context_size": m.context_size,
                    "status": "cached_offline",
                    "details": json.loads(m.details) if m.details else {}
                }
                for m in cached
            ]

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.api_url}/api/tags")
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch models: status {response.status_code}")
                
                data = response.json()
                ollama_models = data.get("models", [])
                
                synced_models = []
                for model_data in ollama_models:
                    name = model_data.get("name")
                    details = model_data.get("details", {})
                    param_size = details.get("parameter_size", "Unknown")
                    
                    # Store model info in DB
                    query = select(ModelInfo).where(ModelInfo.name == name)
                    result = await db.execute(query)
                    db_model = result.scalar_one_or_none()
                    
                    if not db_model:
                        db_model = ModelInfo(
                            name=name,
                            parameter_size=param_size,
                            context_size=8192 if "coder" in name or "llama3" in name else 4096,
                            status="installed",
                            details=json.dumps(model_data)
                        )
                        db.add(db_model)
                    else:
                        db_model.parameter_size = param_size
                        db_model.status = "installed"
                        db_model.details = json.dumps(model_data)
                    
                    synced_models.append({
                        "name": name,
                        "parameter_size": param_size,
                        "context_size": db_model.context_size,
                        "status": "installed",
                        "details": model_data
                    })
                
                await db.commit()
                return synced_models
                
        except Exception as e:
            logger.error(f"Error fetching Ollama models: {e}")
            # Fall back to DB
            result = await db.execute(select(ModelInfo))
            cached = result.scalars().all()
            return [
                {
                    "name": m.name,
                    "parameter_size": m.parameter_size,
                    "context_size": m.context_size,
                    "status": "cached_error",
                    "details": json.loads(m.details) if m.details else {}
                }
                for m in cached
            ]

    async def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        context_window: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completions from local Ollama endpoint"""
        formatted_messages = []
        
        # Inject system prompt if present
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        else:
            formatted_messages.append({"role": "system", "content": settings.DEFAULT_SYSTEM_PROMPT})
            
        formatted_messages.extend(messages)

        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else settings.DEFAULT_TEMPERATURE,
                "num_predict": max_tokens if max_tokens is not None else settings.DEFAULT_MAX_TOKENS,
                "num_ctx": context_window if context_window is not None else settings.DEFAULT_CONTEXT_WINDOW
            }
        }

        logger.info(f"Initiating Ollama chat stream using model '{model}'")
        
        # Define connection retry parameter
        headers = {"Content-Type": "application/json"}
        
        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    f"{self.api_url}/api/chat",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        logger.error(f"Ollama returned HTTP {response.status_code}: {err_text}")
                        yield {
                            "event": "error",
                            "message": f"Ollama returned error status {response.status_code}. Make sure model is downloaded."
                        }
                        return

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        try:
                            chunk = json.loads(line)
                            
                            # Standard Ollama stream fields
                            message_chunk = chunk.get("message", {})
                            token = message_chunk.get("content", "")
                            done = chunk.get("done", False)
                            
                            if done:
                                # We yield done metrics
                                yield {
                                    "event": "done",
                                    "full_content": "",
                                    "prompt_eval_count": chunk.get("prompt_eval_count", 0),
                                    "eval_count": chunk.get("eval_count", 0),
                                    "total_duration": chunk.get("total_duration", 0)
                                }
                            elif token:
                                yield {
                                    "event": "token",
                                    "token": token
                                }
                        except json.JSONDecodeError as je:
                            logger.error(f"Error parsing Ollama response chunk: {je}")
                            continue
                            
        except httpx.ConnectError:
            logger.error("Ollama connection failed. Server not reachable.")
            yield {
                "event": "error",
                "message": "Ollama service offline. Please start Ollama local app."
            }
        except Exception as e:
            logger.error(f"Exception during Ollama streaming: {e}")
            yield {
                "event": "error",
                "message": f"Unexpected error during streaming: {str(e)}"
            }

ollama_service = OllamaService()
