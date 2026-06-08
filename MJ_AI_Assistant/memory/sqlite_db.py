import sqlite3
import json
import struct
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from config.settings import settings

class SQLiteDB:
    def __init__(self, db_path: Path = settings.DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Performance PRAGMAs: WAL mode for concurrent reads, reduced sync overhead, 64MB cache
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
        return conn

    def _initialize_db(self):
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {schema_path}")
            
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self._get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    # --- Conversations management ---
    def create_conversation(self, conversation_id: str, title: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO conversations (conversation_id, title) VALUES (?, ?)",
                (conversation_id, title)
            )
            conn.commit()

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT sender, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC",
                (conversation_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def add_message(self, message_id: str, conversation_id: str, sender: str, content: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (message_id, conversation_id, sender, content) VALUES (?, ?, ?, ?)",
                (message_id, conversation_id, sender, content)
            )
            # Update updated_at on conversation
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE conversation_id = ?",
                (conversation_id,)
            )
            conn.commit()

    # --- Agent Activity Logging ---
    def log_agent_activity(self, agent_name: str, action: str, status: str = "SUCCESS", metrics: Optional[Dict[str, Any]] = None) -> None:
        metrics_json = json.dumps(metrics) if metrics else None
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO agent_logs (agent_name, action_taken, status, metrics) VALUES (?, ?, ?, ?)",
                (agent_name, action, status, metrics_json)
            )
            conn.commit()

    # --- User Preferences ---
    def get_preference(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM user_preferences WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default

    def set_preference(self, key: str, value: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()

    # --- Factual Memories (Vectored Store backup) ---
    def add_raw_memory(self, memory_id: str, fact: str, vector_floats: List[float]) -> None:
        from backend.security.encryption import encrypt_value
        # Encrypt the raw fact before saving to DB
        encrypted_fact = encrypt_value(fact)
        # Serialize vector as binary BLOB (~100x faster than CSV text parsing)
        vector_blob = struct.pack(f'{len(vector_floats)}f', *vector_floats)
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO memories (memory_id, fact, vector) VALUES (?, ?, ?)",
                (memory_id, encrypted_fact, vector_blob)
            )
            conn.commit()

    def get_all_raw_memories(self) -> List[Dict[str, Any]]:
        from backend.security.encryption import decrypt_value
        with self._get_connection() as conn:
            rows = conn.execute("SELECT memory_id, fact, vector FROM memories").fetchall()
            memories = []
            for r in rows:
                blob = r["vector"]
                # Support both legacy CSV text and new binary BLOB formats
                if isinstance(blob, bytes):
                    count = len(blob) // 4
                    vector_floats = list(struct.unpack(f'{count}f', blob))
                else:
                    vector_floats = list(map(float, blob.split(",")))
                
                # Decrypt the fact on read
                try:
                    decrypted_fact = decrypt_value(r["fact"])
                except Exception:
                    # Fallback for unencrypted legacy memories
                    decrypted_fact = r["fact"]
                    
                memories.append({
                    "memory_id": r["memory_id"],
                    "fact": decrypted_fact,
                    "vector": vector_floats
                })
            return memories
            
    def delete_memory(self, memory_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
            conn.commit()
