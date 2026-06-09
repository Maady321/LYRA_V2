import os

schema_path = r"c:\sabari\Lyra\MJ_AI_Assistant\database\schema.sql"

with open(schema_path, "a", encoding="utf-8") as f:
    f.write("""

-- PROMPT FIREWALL V2 LOGS
CREATE TABLE IF NOT EXISTS security_prompt_events (
    event_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    threat_type TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    decision TEXT NOT NULL,
    blocked BOOLEAN NOT NULL,
    reason TEXT
);
""")

print("Schema updated successfully.")
