-- SQLite schema for MJ AI Assistant Database & AIOS Core

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    sender TEXT NOT NULL, -- 'user', 'fury' (coordinator), or individual agents
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_name TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    status TEXT NOT NULL, -- 'SUCCESS', 'FAILED', 'INFO'
    metrics TEXT -- JSON metadata: duration, memory used, tokens, etc.
);

CREATE TABLE IF NOT EXISTS memories (
    memory_id TEXT PRIMARY KEY,
    fact TEXT NOT NULL,
    vector BLOB NOT NULL, -- Binary packed float32 array (nomic-embed-text size = 768)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Virtual table for Full-Text Search FTS5
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    memory_id,
    fact
);

-- Triggers to synchronize memories into FTS5 dynamically
CREATE TRIGGER IF NOT EXISTS insert_memories_fts AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts (memory_id, fact) VALUES (new.memory_id, new.fact);
END;

CREATE TRIGGER IF NOT EXISTS delete_memories_fts AFTER DELETE ON memories BEGIN
    DELETE FROM memories_fts WHERE memory_id = old.memory_id;
END;

CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- FEATURE 1: Knowledge Graph Schemas
CREATE TABLE IF NOT EXISTS graph_entities (
    entity_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL, -- 'user', 'project', 'goal', 'preference', 'task', 'document'
    metadata TEXT, -- JSON metadata string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_relationships (
    relationship_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    predicate TEXT NOT NULL, -- 'studies', 'interested_in', 'owns', 'assigned_to', etc.
    target_id TEXT NOT NULL,
    weight REAL DEFAULT 1.0, -- strength/confidence score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES graph_entities(entity_id) ON DELETE CASCADE,
    FOREIGN KEY(target_id) REFERENCES graph_entities(entity_id) ON DELETE CASCADE,
    UNIQUE(source_id, predicate, target_id)
);

-- FEATURE 2: Autonomous Task Engine Schemas
CREATE TABLE IF NOT EXISTS autonomous_goals (
    goal_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL, -- 'PENDING', 'PLANNING', 'ACTIVE', 'COMPLETED', 'FAILED'
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS autonomous_subtasks (
    subtask_id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    title TEXT NOT NULL,
    assigned_agent TEXT NOT NULL, -- 'STARK', 'BANNER', 'GHOST', etc.
    status TEXT NOT NULL, -- 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'
    execution_result TEXT,
    scheduled_time TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY(goal_id) REFERENCES autonomous_goals(goal_id) ON DELETE CASCADE
);

-- FEATURE 3: GHOST Computer Control Safety Audit Logs
CREATE TABLE IF NOT EXISTS computer_control_audit (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT NOT NULL, -- 'FILE_CREATE', 'CMD_EXECUTE', 'APP_LAUNCH'
    target TEXT NOT NULL,
    command_str TEXT,
    approved_by_user INTEGER DEFAULT 0, -- 1 = Yes, 0 = Pending/Blocked
    security_verdict TEXT NOT NULL -- 'PASSED', 'BLOCKED', 'CONFIRM_PENDING'
);

-- FEATURE 6: AI Workspace Schemas
CREATE TABLE IF NOT EXISTS workspace_notes (
    note_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workspace_projects (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL, -- 'PLANNING', 'ACTIVE', 'ARCHIVED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PHASE 1: GUARDIAN Security Framework Schemas
CREATE TABLE IF NOT EXISTS agent_roles (
    agent_name TEXT PRIMARY KEY,
    trust_level INTEGER DEFAULT 1, -- 1 = Low, 2 = Medium, 3 = High, 4 = System
    role_description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_capabilities (
    capability_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    capability_type TEXT NOT NULL, -- 'FILE_READ', 'FILE_WRITE', 'CMD_EXEC', 'NETWORK_HTTP'
    constraint_pattern TEXT,
    FOREIGN KEY(agent_name) REFERENCES agent_roles(agent_name) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS security_audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actor_agent TEXT NOT NULL,
    target_action TEXT NOT NULL,
    payload_content TEXT NOT NULL, -- Encrypted details
    risk_score REAL NOT NULL,
    verdict TEXT NOT NULL -- 'ALLOWED', 'BLOCKED', 'CONFIRM_PENDING'
);

-- PHASE 2: USER_MODEL Digital Twin Schemas
CREATE TABLE IF NOT EXISTS user_profile (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_skills (
    skill_name TEXT PRIMARY KEY,
    skill_level TEXT NOT NULL, -- 'NOVICE', 'INTERMEDIATE', 'EXPERT'
    confidence_score REAL NOT NULL,
    frequency_used INTEGER DEFAULT 1,
    last_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    associated_tech TEXT,
    status TEXT DEFAULT 'ACTIVE',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



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
