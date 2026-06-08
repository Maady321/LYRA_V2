import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Core Ollama Configuration
    OLLAMA_HOST: str = "http://127.0.0.1:11434"
    PRIMARY_MODEL: str = "llama3:latest"
    FALLBACK_MODEL: str = "mistral:latest"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    
    # Path settings
    LOG_DIR: Path = BASE_DIR / "logs"
    DB_PATH: Path = BASE_DIR / "database" / "mj_assistant.db"
    
    # Agent settings
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    
    # Voice features toggles
    TTS_ENABLED: bool = True
    STT_ENABLED: bool = True
    WAKE_WORD_SENSITIVITY: float = 0.5
    
    # Coqui XTTS v2 Settings
    TTS_ENGINE: str = "xtts"  # "xtts" or "kokoro"
    XTTS_API_URL: str = "http://127.0.0.1:8020"
    XTTS_SPEAKER: str = "Claribel Dervla"
    XTTS_LANGUAGE: str = "en"
    
    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

# Create required directories on import
Settings().LOG_DIR.mkdir(parents=True, exist_ok=True)
Settings().DB_PATH.parent.mkdir(parents=True, exist_ok=True)

settings = Settings()
