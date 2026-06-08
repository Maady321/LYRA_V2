import re
import logging
from enum import Enum
from typing import Tuple
from backend.security.intrusion_detection import ids_monitor

logger = logging.getLogger("PromptFirewall")

class ThreatLevel(Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PromptInjectionDetected(Exception):
    pass

class PromptFirewall:
    """
    Enterprise Prompt Firewall
    Scans incoming user prompts for known injection vectors, jailbreaks, and system extraction attempts.
    """
    
    JAILBREAK_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?previous\s+instructions",
        r"(?i)system\s+prompt",
        r"(?i)you\s+are\s+now\s+(a\s+)?(developer|admin|root|DAN)",
        r"(?i)bypass\s+(all\s+)?rules",
        r"(?i)disregard\s+(all\s+)?prior",
        r"(?i)forget\s+(all\s+)?commands",
        r"(?i)print\s+(your\s+)?instructions",
        r"(?i)what\s+are\s+your\s+instructions",
        r"(?i)act as an unrestricted"
    ]
    
    DANGEROUS_CMD_PATTERNS = [
        r"(?i)os\.system",
        r"(?i)subprocess\.Popen",
        r"(?i)rm\s+-rf",
        r"(?i)del\s+/f",
        r"(?i)drop\s+table",
        r"(?i)truncate\s+table",
        r"(?i)eval\(",
        r"(?i)exec\("
    ]

    @classmethod
    def evaluate_prompt(cls, user_id: str, prompt: str) -> Tuple[ThreatLevel, str]:
        """
        Evaluates a prompt and returns the ThreatLevel and an optional block reason.
        """
        if not prompt:
            return ThreatLevel.SAFE, ""
            
        # 1. Check for Jailbreaks / System Prompt Extraction
        for pattern in cls.JAILBREAK_PATTERNS:
            if re.search(pattern, prompt):
                ids_monitor.record_prompt_injection(user_id)
                logger.warning(f"[FIREWALL] Jailbreak detected from {user_id}: {pattern}")
                return ThreatLevel.CRITICAL, "Prompt injection / jailbreak attempt detected."
                
        # 2. Check for Direct Code Execution Injection
        for pattern in cls.DANGEROUS_CMD_PATTERNS:
            if re.search(pattern, prompt):
                ids_monitor.record_agent_violation(user_id, "MALICIOUS_CMD_INJECTION")
                logger.warning(f"[FIREWALL] Dangerous command injection from {user_id}: {pattern}")
                return ThreatLevel.CRITICAL, "Malicious code execution payload detected."
                
        # 3. Length checks (often used for buffer overflow / DOS attacks on LLMs)
        if len(prompt) > 5000:
            logger.warning(f"[FIREWALL] Oversized prompt from {user_id} ({len(prompt)} chars)")
            return ThreatLevel.HIGH, "Prompt exceeds maximum allowed length."
            
        return ThreatLevel.SAFE, ""

prompt_firewall = PromptFirewall()

def inspect_prompt(prompt_text: str) -> bool:
    """Legacy wrapper for compatibility"""
    level, reason = prompt_firewall.evaluate_prompt("API_User", prompt_text)
    if level == ThreatLevel.CRITICAL:
        raise PromptInjectionDetected(reason)
    return True
