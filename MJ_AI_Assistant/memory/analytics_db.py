import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from MJ_AI_Assistant.security.guardian import guardian_kernel

class AnalyticsDB:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).parent.parent / "database" / "analytics.db"
        self._initialize_db()

    def _get_connection(self):
        guardian_kernel.authorize_execution(agent_name="analytics_db", action="db_access", target="sqlite3")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self):
        schema_path = Path(__file__).parent.parent / "database" / "analytics_schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Analytics Schema not found at {schema_path}")
            
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self._get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    def log_performance(
        self, 
        agent_name: str, 
        latency_ms: int, 
        prompt_tokens: int = 0, 
        completion_tokens: int = 0, 
        memory_usage_mb: float = 0.0, 
        success: bool = True
    ) -> None:
        """
        Logs detailed resource telemetry for a specific agent execution.
        """
        status = "SUCCESS" if success else "FAILED"
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO agent_performance 
                   (agent_name, latency_ms, prompt_tokens, completion_tokens, memory_usage_mb, success_status) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (agent_name.upper(), latency_ms, prompt_tokens, completion_tokens, memory_usage_mb, status)
            )
            conn.commit()

    def get_agent_rankings(self) -> List[Dict[str, Any]]:
        """
        Calculates agent utilization and success rates from logged telemetry.
        """
        query = """
        SELECT agent_name, 
               COUNT(*) as total_tasks, 
               AVG(latency_ms) as avg_latency, 
               SUM(prompt_tokens + completion_tokens) as total_tokens,
               SUM(CASE WHEN success_status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
        FROM agent_performance
        GROUP BY agent_name
        ORDER BY total_tasks DESC
        """
        with self._get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    def log_behavioral_insight(self, insight_type: str, summary: str, metrics: Optional[Dict[str, Any]] = None) -> None:
        import uuid
        insight_id = f"insight_{uuid.uuid4().hex[:8]}"
        metrics_json = json.dumps(metrics) if metrics else None
        
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO behavioral_insights (insight_id, insight_type, summary, metrics) 
                   VALUES (?, ?, ?, ?)""",
                (insight_id, insight_type.upper(), summary, metrics_json)
            )
            conn.commit()

    def get_behavioral_insights(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT timestamp, insight_type, summary, metrics FROM behavioral_insights ORDER BY timestamp DESC"
            ).fetchall()
            return [dict(r) for r in rows]
