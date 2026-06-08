-- SQLite schema for Agent Performance & Telemetry Diagnostics

CREATE TABLE IF NOT EXISTS agent_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_name TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    memory_usage_mb REAL NOT NULL,
    success_status TEXT NOT NULL -- 'SUCCESS', 'FAILED'
);

CREATE TABLE IF NOT EXISTS behavioral_insights (
    insight_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insight_type TEXT NOT NULL, -- 'PRODUCTIVITY', 'HABITS', 'GOAL_TIMELINE'
    summary TEXT NOT NULL,
    metrics TEXT -- JSON representation of specific tracked metrics
);
