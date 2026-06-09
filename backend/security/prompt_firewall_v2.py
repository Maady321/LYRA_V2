import re
import hashlib
from typing import Dict, Any, Tuple
from datetime import datetime
import uuid

# Define Risk Levels
RISK_LEVELS = {
    "SAFE": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

# Define Threat Categories and their heuristics
THREAT_PATTERNS = {
    "PRIVILEGE_ESCALATION": {
        "level": "CRITICAL",
        "patterns": [
            r"act\s+as\s+admin",
            r"act\s+as\s+system",
            r"you\s+are\s+(ghost|system|admin|administrator|root)",
            r"become\s+administrator",
            r"assume\s+root\s+access"
        ]
    },
    "PROMPT_INJECTION": {
        "level": "HIGH",
        "patterns": [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"disregard\s+all\s+rules",
            r"forget\s+system\s+policies",
            r"override\s+safeguards",
            r"ignore\s+guardian"
        ]
    },
    "SECURITY_BYPASS": {
        "level": "CRITICAL",
        "patterns": [
            r"bypass\s+(guardian|rbac|security)",
            r"disable\s+(firewall|security)",
            r"ignore\s+rbac",
            r"turn\s+off\s+security"
        ]
    },
    "FILE_DESTRUCTION": {
        "level": "CRITICAL",
        "patterns": [
            r"delete\s+all\s+files",
            r"erase\s+workspace",
            r"remove\s+directory",
            r"delete\s+[a-zA-Z]:\\",
            r"wipe\s+folder",
            r"remove\s+every\s+document",
            r"erase\s+all\s+data",
            r"wipe\s+storage",
            r"destroy\s+everything",
            r"rm\s+-rf"
        ]
    },
    "DATABASE_DESTRUCTION": {
        "level": "CRITICAL",
        "patterns": [
            r"drop\s+database",
            r"drop\s+table",
            r"delete\s+memories",
            r"erase\s+knowledge\s+graph",
            r"remove\s+all\s+records"
        ]
    },
    "SECRET_EXTRACTION": {
        "level": "HIGH",
        "patterns": [
            r"list\s+(every\s+|all\s+)?api\s+key",
            r"show\s+credentials",
            r"reveal\s+(all\s+)?secrets?",
            r"print\s+tokens",
            r"show\s+secret\s+memories"
        ]
    },
    "DATA_EXFILTRATION": {
        "level": "HIGH",
        "patterns": [
            r"export\s+all\s+memories",
            r"show\s+classified\s+memories",
            r"print\s+encrypted\s+data"
        ]
    },
    "SOCIAL_ENGINEERING": {
        "level": "HIGH",
        "patterns": [
            r"pretend\s+guardian\s+approved\s+this",
            r"assume\s+user\s+authorization",
            r"emergency\s+override"
        ]
    }
}

class PromptFirewallV2:
    def __init__(self, db_connection=None):
        """
        Initializes the firewall. If a db_connection is provided, it will log audits directly.
        (Usually we pass the db layer instance so the firewall can write to security_prompt_events).
        """
        self.db = db_connection

    def analyze_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Analyzes prompt and returns detected threats.
        """
        detected_threats = []
        highest_risk = "SAFE"
        normalized_prompt = prompt.lower().strip()
        
        # We replace multiple spaces with single space for better regex matching
        normalized_prompt = re.sub(r'\s+', ' ', normalized_prompt)

        for category, rules in THREAT_PATTERNS.items():
            for pattern in rules["patterns"]:
                if re.search(pattern, normalized_prompt):
                    detected_threats.append({
                        "category": category,
                        "level": rules["level"],
                        "matched_pattern": pattern
                    })
                    if RISK_LEVELS[rules["level"]] > RISK_LEVELS[highest_risk]:
                        highest_risk = rules["level"]

        return {
            "highest_risk": highest_risk,
            "threats": detected_threats
        }

    def sanitize(self, prompt: str, threats: list) -> str:
        """
        Attempts to sanitize lower level threats. 
        Note: HIGH and CRITICAL are hard blocked, so sanitization is mostly for MEDIUM/LOW.
        """
        sanitized = prompt
        # Replace detected dangerous patterns with [REDACTED]
        for t in threats:
            pattern = t["matched_pattern"]
            sanitized = re.sub(pattern, "[REDACTED_SECURITY_POLICY]", sanitized, flags=re.IGNORECASE)
        return sanitized

    def make_decision(self, risk_level: str) -> Tuple[str, str]:
        """
        Returns (Decision, Reason)
        """
        if risk_level == "SAFE":
            return ("ALLOW", "Prompt is safe.")
        elif risk_level == "LOW":
            return ("ALLOW", "Low risk intent detected. Allowed but logged.")
        elif risk_level == "MEDIUM":
            return ("ALLOW", "Medium risk intent detected. Allowed with warning.")
        elif risk_level in ["HIGH", "CRITICAL"]:
            return ("BLOCKED", f"Severe destructive or manipulative operation detected (Risk: {risk_level}).")
        
        return ("BLOCKED", "Unknown risk level.")

    def inspect_prompt(self, user: str, prompt: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Primary entrypoint for the firewall.
        Returns: (is_allowed: bool, response_string: str, audit_data: dict)
        """
        # 1. Analyze
        analysis = self.analyze_intent(prompt)
        risk_level = analysis["highest_risk"]
        
        # 2. Decide
        decision, reason = self.make_decision(risk_level)
        
        # 3. Sanitize if allowed but risky
        final_prompt = prompt
        if decision == "ALLOW" and risk_level != "SAFE":
            final_prompt = self.sanitize(prompt, analysis["threats"])
            
        is_blocked = (decision == "BLOCKED")
        
        # 4. Generate Audit payload
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        event_id = str(uuid.uuid4())
        
        threat_type = "NONE"
        if analysis["threats"]:
            # Pick highest threat type to report
            analysis["threats"].sort(key=lambda x: RISK_LEVELS[x["level"]], reverse=True)
            threat_type = analysis["threats"][0]["category"]

        audit_data = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "prompt_hash": prompt_hash,
            "threat_type": threat_type,
            "risk_level": risk_level,
            "decision": decision,
            "blocked": is_blocked,
            "reason": reason
        }
        
        # Log to Database if available
        if self.db and hasattr(self.db, "log_prompt_event"):
            try:
                self.db.log_prompt_event(audit_data)
            except Exception as e:
                print(f"[FIREWALL] Error logging audit: {e}")
        
        # 5. Format Response
        if is_blocked:
            block_response = (
                f"SECURITY ALERT\n\n"
                f"Threat Type:\n{threat_type}\n\n"
                f"Risk Level:\n{risk_level}\n\n"
                f"Decision:\n{decision}\n\n"
                f"Reason:\n{reason}\n\n"
                f"Event ID: {event_id}\n"
            )
            return False, block_response, audit_data
            
        return True, final_prompt, audit_data

# Instantiate a global instance for places that don't pass the DB immediately
prompt_firewall = PromptFirewallV2()
