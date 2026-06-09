import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from config.settings import settings
from MJ_AI_Assistant.security.guardian import guardian_kernel

class OracleRouter:
    def __init__(self, db_path: Path = settings.DB_PATH, ollama_client=None):
        self.db_path = db_path
        self.client = ollama_client
        self._initialize_oracle_tables()

    def _initialize_oracle_tables(self):
        """
        Builds the model registry and performance tracking tables if not already present.
        """
        guardian_kernel.authorize_execution(agent_name="oracle", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS local_models_registry (
                    model_name TEXT PRIMARY KEY,
                    specialty_tag TEXT NOT NULL,
                    performance_score REAL DEFAULT 0.8,
                    is_installed INTEGER DEFAULT 0
                   )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS model_performance_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    tokens_per_sec REAL NOT NULL,
                    status TEXT NOT NULL
                   )"""
            )
            
            # Seed standard local model mapping guidelines
            mappings = [
                ("qwen2.5-coder:7b", "CODING", 0.95, 1),
                ("llava:latest", "VISION", 0.90, 1),
                ("deepseek-coder:6.7b", "REASONING", 0.92, 1),
                ("llama3:latest", "CHAT", 0.85, 1),
                ("nomic-embed-text", "EMBEDDINGS", 0.99, 1)
            ]
            for name, spec, perf, inst in mappings:
                conn.execute(
                    "INSERT OR IGNORE INTO local_models_registry (model_name, specialty_tag, performance_score, is_installed) VALUES (?, ?, ?, ?)",
                    (name, spec, perf, inst)
                )
            conn.commit()

    def route_task(self, task_type: str, prompt_text: str) -> str:
        """
        Determines the optimal local LLM or vision adapter based on the task description.
        If the primary candidate is not running, falls back safely to first active model.
        """
        task_upper = task_type.upper().strip()
        
        guardian_kernel.authorize_execution(agent_name="oracle", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT model_name FROM local_models_registry WHERE specialty_tag = ? AND is_installed = 1",
                (task_upper,)
            ).fetchone()
            
        primary_candidate = row["model_name"] if row else "llama3:latest"
        
        # Pull running models from Ollama to ensure active presence
        if self.client:
            try:
                installed_models = self.client.list_local_models()
                if primary_candidate in installed_models:
                    return primary_candidate
                    
                # Graceful fallback logic
                if installed_models:
                    fallback = installed_models[0]
                    print(f"[ORACLE] Requested model '{primary_candidate}' not found. Falling back to active: '{fallback}'")
                    return fallback
            except Exception as e:
                print(f"[ORACLE] Failed to query Ollama registry: {e}. Defaulting to primary candidate.")
                
        return primary_candidate

    def log_metrics(self, model_name: str, task_type: str, tokens_per_sec: float, status: str = "SUCCESS") -> None:
        """
        Logs runtime latency and execution status of the routed model.
        """
        guardian_kernel.authorize_execution(agent_name="oracle", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO model_performance_logs (model_name, task_type, tokens_per_sec, status) VALUES (?, ?, ?, ?)",
                (model_name, task_type, tokens_per_sec, status)
            )
            conn.commit()
