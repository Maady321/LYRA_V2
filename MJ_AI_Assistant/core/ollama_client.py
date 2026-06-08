import json
import httpx
from typing import List, Dict, Any, AsyncGenerator, Optional
from config.settings import settings

class OllamaClient:
    def __init__(self, host: str = settings.OLLAMA_HOST):
        self.host = host.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)

    async def is_online(self) -> bool:
        try:
            res = await self.client.get(f"{self.host}/api/tags")
            return res.status_code == 200
        except Exception:
            return False

    async def list_local_models(self) -> List[str]:
        try:
            res = await self.client.get(f"{self.host}/api/tags")
            if res.status_code == 200:
                data = res.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception:
            return []

    async def generate_embedding(self, text: str, model: str = settings.EMBEDDING_MODEL) -> List[float]:
        """
        Generates clean embedding float vectors from Ollama embeddings API endpoint.
        """
        try:
            payload = {"model": model, "prompt": text}
            res = await self.client.post(f"{self.host}/api/embeddings", json=payload, timeout=10.0)
            if res.status_code == 200:
                return res.json().get("embedding", [])
            
            # Fallback to primary model if embedding model is not downloaded
            payload["model"] = settings.PRIMARY_MODEL
            res = await self.client.post(f"{self.host}/api/embeddings", json=payload, timeout=10.0)
            if res.status_code == 200:
                return res.json().get("embedding", [])
                
            return []
        except Exception as e:
            print(f"[OllamaClient] Embedding generation failure: {e}")
            return []

    async def generate_chat_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = settings.PRIMARY_MODEL,
        stream: bool = False,
        temperature: float = settings.DEFAULT_TEMPERATURE
    ) -> Any:
        """
        Generates chat completions, falling back automatically if the target model triggers an error.
        """
        url = f"{self.host}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

        try:
            # 1. Try primary request
            if stream:
                return self._stream_request(url, payload)
            else:
                res = await self.client.post(url, json=payload, timeout=60.0)
                if res.status_code == 200:
                    return res.json().get("message", {}).get("content", "")
                raise httpx.HTTPStatusError("HTTP Error", request=res.request, response=res)
        except Exception as e:
            print(f"[OllamaClient] Model '{model}' failed or offline: {e}. Trying fallback model...")
            
            # 2. Trigger fallback model
            payload["model"] = settings.FALLBACK_MODEL
            try:
                if stream:
                    return self._stream_request(url, payload)
                else:
                    res = await self.client.post(url, json=payload, timeout=60.0)
                    if res.status_code == 200:
                        return res.json().get("message", {}).get("content", "")
                    return "Error: Local Ollama orchestrator and fallback models are offline."
            except Exception as fe:
                return f"Error: Core LLM engine connection failure. Details: {fe}"

    async def _stream_request(self, url: str, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as r:
                if r.status_code != 200:
                    yield "Error contacting local model server."
                    return
                async for line in r.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            if token:
                                yield token
                        except Exception:
                            continue
