import re
import logging
from enum import Enum
from typing import Tuple
from backend.security.intrusion_detection import ids_monitor

logger = logging.getLogger("VoiceGuardian")

class VoiceRiskCategory(Enum):
    SAFE = "SAFE"
    SENSITIVE = "SENSITIVE"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"

class VoiceGuardian:
    """
    Analyzes spoken commands (converted to text) to ensure highly destructive 
    or sensitive actions require an explicit authorization step before execution.
    """
    
    AUTHORIZATION_PHRASE = "authorize lyra"
    
    CRITICAL_KEYWORDS = [
        "delete", "remove", "format", "shutdown", "reboot",
        "drop", "wipe", "uninstall", "destroy", "kill"
    ]
    
    SENSITIVE_KEYWORDS = [
        "read my emails", "open passwords", "credit card", "bank",
        "send money", "purchase", "buy"
    ]

    @classmethod
    def categorize_transcript(cls, transcript: str) -> VoiceRiskCategory:
        text = transcript.lower()
        
        for word in cls.CRITICAL_KEYWORDS:
            if re.search(r'\b' + word + r'\b', text):
                return VoiceRiskCategory.CRITICAL
                
        for word in cls.SENSITIVE_KEYWORDS:
            if re.search(r'\b' + word + r'\b', text):
                return VoiceRiskCategory.SENSITIVE
                
        return VoiceRiskCategory.SAFE

    @classmethod
    def validate_command(cls, transcript: str, is_authorized: bool = False) -> Tuple[bool, str]:
        """
        Validates whether a transcript should be allowed.
        If it's CRITICAL and lacks the authorization phrase, it is blocked.
        """
        category = cls.categorize_transcript(transcript)
        
        if category == VoiceRiskCategory.CRITICAL:
            if cls.AUTHORIZATION_PHRASE in transcript.lower() or is_authorized:
                logger.info(f"[VOICE GUARDIAN] Authorized CRITICAL execution: {transcript}")
                return True, "Authorized"
            else:
                logger.warning(f"[VOICE GUARDIAN] Blocked unauthorized CRITICAL execution: {transcript}")
                ids_monitor.record_agent_violation("VOICE_USER", "UNAUTHORIZED_CRITICAL_VOICE_COMMAND")
                return False, f"CRITICAL action requires the phrase: '{cls.AUTHORIZATION_PHRASE}' to proceed."
                
        return True, "Safe"

voice_guardian = VoiceGuardian()
