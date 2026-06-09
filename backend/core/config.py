import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base workspace path (backend/ directory)
BASE_DIR = Path(__file__).resolve().parent.parent
# Project root (Lyra workspace root, parent of backend/)
WORKSPACE_ROOT = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lyra AI"
    API_V1_STR: str = "/api"
    DEBUG_SECURITY: bool = False
    
    # Workspace path (project root)
    WORKSPACE_PATH: str = str(WORKSPACE_ROOT)
    
    # MJ AI Assistant database path
    MJ_ASSISTANT_DB: str = str(WORKSPACE_ROOT / "MJ_AI_Assistant" / "database" / "mj_assistant.db")
    
    # SQLite Database Configuration
    DB_FILE: str = str(BASE_DIR / "lyra.db")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.DB_FILE}"
        
    # Ollama Service
    OLLAMA_API_URL: str = "http://127.0.0.1:11434"
    OLLAMA_TIMEOUT: float = 120.0
    
    # AI Generation Defaults
    DEFAULT_MODEL: str = "llama3"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048
    DEFAULT_CONTEXT_WINDOW: int = 4096
    DEFAULT_SYSTEM_PROMPT: str = (
        "You are Lyra, a sophisticated, hyper-intelligent, local desktop AI assistant. "
        "Your responses should be precise, clear, and elegant. Code should be formatted with "
        "proper markdown syntax highlighting."
    )
    
    # WebSocket config
    WS_HEARTBEAT_INTERVAL: float = 30.0
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
