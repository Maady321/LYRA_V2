from enum import Enum
import re

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# Common dangerous commands in powershell/cmd/bash
CRITICAL_PATTERNS = [
    r"(?i)\bformat\s+[c-z]:",
    r"(?i)\bdel\s+(/s|/f|/q)*\s*[c-z]:\\Windows",
    r"(?i)\brmdir\s+(/s|/q)*\s*[c-z]:\\Windows",
    r"(?i)\brm\s+-rf\s+/",
    r"(?i)Stop-Computer",
    r"(?i)Restart-Computer",
    r"(?i)net\s+user\s+.*\s+/add",
]

HIGH_PATTERNS = [
    r"(?i)\bdel\s+(/s|/f|/q)*\s+.*\.(db|sqlite|key|env)",
    r"(?i)\brm\s+-rf\s+.*",
    r"(?i)DROP\s+TABLE",
    r"(?i)DELETE\s+FROM",
]

def assess_risk(action: str, payload: str) -> RiskLevel:
    """
    Evaluates the risk level of an action and its payload payload.
    """
    combined_text = f"{action} {payload}".strip()

    # Check for Critical Patterns
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, combined_text):
            return RiskLevel.CRITICAL
            
    # Check for High Patterns
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, combined_text):
            return RiskLevel.HIGH

    # Contextual Classification
    action_lower = action.lower()
    
    if action_lower in ["execute_script", "run_command", "modify_database", "delete_file"]:
        return RiskLevel.HIGH
        
    if action_lower in ["open_file", "browser_access", "write_file"]:
        return RiskLevel.MEDIUM
        
    # Default fallback
    return RiskLevel.LOW
