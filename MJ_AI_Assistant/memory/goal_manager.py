import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from memory.sqlite_db import SQLiteDB
from MJ_AI_Assistant.security.guardian import guardian_kernel

class AutonomousGoalManager:
    def __init__(self, db: SQLiteDB):
        self.db = db

    def register_goal(self, title: str, description: str = "", priority: int = 1) -> str:
        """
        Creates an autonomous high-level goal block inside the scheduler.
        """
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        guardian_kernel.authorize_execution(agent_name="goal_manager", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                """INSERT INTO autonomous_goals (goal_id, title, description, status, priority) 
                   VALUES (?, ?, ?, ?, ?)""",
                (goal_id, title, description, "PENDING", priority)
            )
            conn.commit()
        return goal_id

    def add_subtask(self, goal_id: str, title: str, assigned_agent: str, scheduled_time: Optional[str] = None) -> str:
        """
        Appends an executable subtask linked directly to a goal.
        """
        subtask_id = f"subtask_{uuid.uuid4().hex[:8]}"
        sched = scheduled_time or datetime.utcnow().isoformat()
        guardian_kernel.authorize_execution(agent_name="goal_manager", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                """INSERT INTO autonomous_subtasks (subtask_id, goal_id, title, assigned_agent, status, scheduled_time) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (subtask_id, goal_id, title, assigned_agent.upper(), "PENDING", sched)
            )
            conn.commit()
        return subtask_id

    def get_pending_subtasks(self) -> List[Dict[str, Any]]:
        """
        Extracts subtasks scheduled for immediate execution.
        """
        query = """
        SELECT s.subtask_id, s.goal_id, s.title, s.assigned_agent, g.title as goal_title 
        FROM autonomous_subtasks s
        JOIN autonomous_goals g ON s.goal_id = g.goal_id
        WHERE s.status = 'PENDING' AND datetime(s.scheduled_time) <= datetime('now')
        ORDER BY g.priority DESC, s.scheduled_time ASC
        """
        guardian_kernel.authorize_execution(agent_name="goal_manager", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    def update_subtask_status(self, subtask_id: str, status: str, result: Optional[str] = None) -> None:
        """
        Updates task completions and records output results.
        """
        now = datetime.utcnow().isoformat() if status == "COMPLETED" else None
        guardian_kernel.authorize_execution(agent_name="goal_manager", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                """UPDATE autonomous_subtasks 
                   SET status = ?, execution_result = ?, completed_at = ? 
                   WHERE subtask_id = ?""",
                (status, result, now, subtask_id)
            )
            conn.commit()
            
            # Auto complete parent goal if all subtasks are finished!
            cursor = conn.execute(
                "SELECT goal_id FROM autonomous_subtasks WHERE subtask_id = ?", (subtask_id,)
            )
            row = cursor.fetchone()
            if row:
                goal_id = row[0]
                cursor_check = conn.execute(
                    "SELECT COUNT(*) FROM autonomous_subtasks WHERE goal_id = ? AND status != 'COMPLETED'",
                    (goal_id,)
                )
                remaining = cursor_check.fetchone()[0]
                if remaining == 0:
                    conn.execute(
                        "UPDATE autonomous_goals SET status = 'COMPLETED' WHERE goal_id = ?",
                        (goal_id,)
                    )
                    conn.commit()
