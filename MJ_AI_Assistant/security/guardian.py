import sqlite3
import re
import base64
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from config.settings import settings

class GuardianAgent:
    def __init__(self, db_path: Path = settings.DB_PATH):
        self.db_path = db_path
        self.injection_patterns = [
            re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+a\s+bypass", re.IGNORECASE),
            re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
            re.compile(r"dan\s+mode\s+active", re.IGNORECASE),
            re.compile(r"disregard\s+prior\s+rules", re.IGNORECASE)
        ]
        self.dangerous_commands = [
            re.compile(r"\b(rm|del|rmdir)\s+-rf\b", re.IGNORECASE),
            re.compile(r"\bformat\s+[c-z]:\b", re.IGNORECASE),
            re.compile(r"\b(shred|regedit)\b", re.IGNORECASE),
            re.compile(r"\bpowershell\s+-[eE](ncodedCommand)?\b", re.IGNORECASE)
        ]
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """
        Seeds default agent roles and capability permissions into the SQLite schema.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            # 1. Seed Roles
            roles = [
                ("FURY", 4, "System Coordinator Agent"),
                ("VISION", 3, "Memory Agent"),
                ("CAPTAIN", 3, "Planning Agent"),
                ("BANNER", 2, "Research Agent"),
                ("STARK", 2, "Sandboxed Execution Agent"),
                ("JARVIS", 3, "Monitoring Agent"),
                ("SPIDEY", 2, "Notification Agent"),
                ("GHOST", 2, "Audited Computer Control Agent"),
                ("EAGLE", 2, "Vision and OCR Interpreter Agent")
            ]
            for name, level, desc in roles:
                conn.execute(
                    "INSERT OR IGNORE INTO agent_roles (agent_name, trust_level, role_description) VALUES (?, ?, ?)",
                    (name, level, desc)
                )
            
            # 2. Seed Capabilities
            capabilities = [
                ("cap_fury_chat", "FURY", "CHAT", None),
                ("cap_vision_read", "VISION", "FILE_READ", None),
                ("cap_vision_write", "VISION", "FILE_WRITE", None),
                ("cap_banner_read", "BANNER", "FILE_READ", None),
                ("cap_stark_exec", "STARK", "CMD_EXEC", None),
                ("cap_ghost_exec", "GHOST", "CMD_EXEC", None),
                ("cap_eagle_read", "EAGLE", "FILE_READ", None)
            ]
            for cap_id, agent, cap_type, pattern in capabilities:
                conn.execute(
                    "INSERT OR IGNORE INTO agent_capabilities (capability_id, agent_name, capability_type, constraint_pattern) VALUES (?, ?, ?, ?)",
                    (cap_id, agent, cap_type, pattern)
                )
            conn.commit()

    def validate_action(self, agent_name: str, action_type: str, payload: str) -> Tuple[str, float, str]:
        """
        Validates prompt inputs and system execution payloads.
        Returns a tuple of (verdict, risk_score, reasoning).
        """
        agent_upper = agent_name.upper().strip()
        
        # 1. Audit prompt injections in chat queries
        for pattern in self.injection_patterns:
            if pattern.search(payload):
                self.log_security_audit(agent_upper, action_type, payload, 1.0, "BLOCKED")
                return "BLOCKED", 1.0, f"Prompt injection pattern matched: '{pattern.pattern}'"

        # 2. Audit malicious OS commands
        if action_type == "CMD_EXEC":
            for pattern in self.dangerous_commands:
                if pattern.search(payload):
                    self.log_security_audit(agent_upper, action_type, payload, 1.0, "BLOCKED")
                    return "BLOCKED", 1.0, f"Dangerous command pattern intercepted: '{pattern.pattern}'"

        # 3. Check RBAC permissions in SQLite
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            role = conn.execute("SELECT trust_level FROM agent_roles WHERE agent_name = ?", (agent_upper,)).fetchone()
            if not role:
                self.log_security_audit(agent_upper, action_type, payload, 0.9, "BLOCKED")
                return "BLOCKED", 0.9, f"Agent '{agent_upper}' is unregistered under the system RBAC kernel."

            trust_level = role["trust_level"]
            
            # Query if capability exists
            cap = conn.execute(
                "SELECT constraint_pattern FROM agent_capabilities WHERE agent_name = ? AND capability_type = ?",
                (agent_upper, action_type)
            ).fetchone()
            
            if not cap:
                self.log_security_audit(agent_upper, action_type, payload, 0.8, "BLOCKED")
                return "BLOCKED", 0.8, f"Agent '{agent_upper}' lacks capability permission: '{action_type}'"

        # 4. Compute risk scoring heuristic
        risk_score = 0.0
        if trust_level < 3:
            risk_score += 0.2
        if action_type in ["CMD_EXEC", "FILE_WRITE"]:
            risk_score += 0.35
            
        verdict = "ALLOWED" if risk_score < 0.45 else "CONFIRM_PENDING"
        self.log_security_audit(agent_upper, action_type, payload, risk_score, verdict)
        return verdict, risk_score, "Transaction passed all core security boundaries."

    def log_security_audit(self, actor: str, action: str, payload: str, risk: float, verdict: str) -> None:
        """
        Encrypts payload content (obfuscates via base64) and writes entry to audit logs.
        """
        payload_bytes = payload.encode('utf-8')
        encoded_payload = base64.b64encode(payload_bytes).decode('utf-8')
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO security_audit_logs (actor_agent, target_action, payload_content, risk_score, verdict)
                   VALUES (?, ?, ?, ?, ?)""",
                (actor, action, encoded_payload, risk, verdict)
            )
            conn.commit()
