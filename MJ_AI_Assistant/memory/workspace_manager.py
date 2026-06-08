import sqlite3
import uuid
from typing import List, Dict, Any, Optional
from memory.sqlite_db import SQLiteDB

class AIWorkspaceManager:
    def __init__(self, db: SQLiteDB):
        self.db = db

    # --- Markdown Notes ---
    def create_note(self, title: str, content: str = "") -> str:
        note_id = f"note_{uuid.uuid4().hex[:8]}"
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT INTO workspace_notes (note_id, title, content) VALUES (?, ?, ?)",
                (note_id, title, content)
            )
            conn.commit()
        return note_id

    def search_notes_full_text(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Conducts full-text searches inside SQLite notes using LIKE mapping indexes.
        """
        query = "SELECT note_id, title, content, updated_at FROM workspace_notes WHERE content LIKE ? OR title LIKE ?"
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, (f"%{search_term}%", f"%{search_term}%")).fetchall()
            return [dict(r) for r in rows]

    # --- Project management ---
    def create_project(self, title: str, description: str = "") -> str:
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "INSERT INTO workspace_projects (project_id, title, description, status) VALUES (?, ?, ?, ?)",
                (project_id, title, description, "PLANNING")
            )
            conn.commit()
        return project_id

    def list_active_projects(self) -> List[Dict[str, Any]]:
        query = "SELECT project_id, title, description, status, created_at FROM workspace_projects WHERE status != 'ARCHIVED'"
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]
