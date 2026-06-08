import logging
import re
from typing import Dict, Any, List, Optional
from core.redis_broker import Task

logger = logging.getLogger("GuardianV2")

class SecurityViolation(Exception):
    pass

class EnterpriseGuardian:
    """
    Zero-Trust Security layer for Lyra AIOS.
    Implements Role-Based Access Control (RBAC), Prompt Injection heuristics, 
    and Secrets masking before any task is routed to a worker agent.
    """
    def __init__(self):
        self.injection_patterns = [
            r"(?i)(ignore previous instructions|disregard|system prompt)",
            r"(?i)(you are now|act as an unconstrained|DAN|do anything now)",
            r"(?i)(bypass|override|disable)(.*)(security|filters)",
            r"([A-Za-z0-9+/]{100,}={0,2})", # Base64 obfuscation heuristics
        ]
        
    async def validate_task(self, task: Task) -> bool:
        """Core Zero-Trust validation checkpoint for all incoming tasks."""
        try:
            # 1. Prompt Injection & Jailbreak Detection
            self._scan_for_injection(task.goal)
            if isinstance(task.payload, dict):
                for k, v in task.payload.items():
                    if isinstance(v, str):
                        self._scan_for_injection(v)
            
            # 2. RBAC / ABAC Check
            await self._verify_rbac(task.assigner, task.assignee, task.goal)
            
            # 3. Data Loss Prevention (Secrets Masking)
            task.goal = self._mask_secrets(task.goal)
            
            return True
            
        except SecurityViolation as e:
            logger.critical(f"SECURITY VIOLATION DETECTED: {e}")
            # In an enterprise setting, forward to Loki or SIEM
            task.status = "FAILED"
            task.result = f"Security Violation: {e}"
            return False

    def _scan_for_injection(self, text_input: str):
        for pattern in self.injection_patterns:
            if re.search(pattern, text_input):
                raise SecurityViolation("Prompt Injection or Jailbreak attempt detected.")

    async def _verify_rbac(self, assigner: str, assignee: str, intent: str):
        """
        Check if the 'assigner' has the role permission to invoke 'assignee' 
        for the given 'intent' level.
        """
        # Hardcode some high-level isolation rules
        if assigner == "EXTERNAL_USER" and assignee == "GHOST":
            # GHOST handles OS shell, must require explicit FURY or GUARDIAN proxy
            raise SecurityViolation("External users cannot directly invoke OS-level agents.")
        
        if assignee == "GUARDIAN":
            raise SecurityViolation("Agents cannot recursively invoke the Guardian.")

    def _mask_secrets(self, text_input: str) -> str:
        """Regex-based Data Loss Prevention (DLP) for common secrets."""
        # Mask AWS Keys
        text_input = re.sub(r"(?i)(AKIA[0-9A-Z]{16})", "[MASKED_AWS_KEY]", text_input)
        # Mask RSA Keys
        text_input = re.sub(r"-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----", "[MASKED_RSA_KEY]", text_input, flags=re.DOTALL)
        # Mask basic Authorization Bearer tokens
        text_input = re.sub(r"(?i)bearer\s+[a-zA-Z0-9\-\._~+/]+", "Bearer [MASKED_TOKEN]", text_input)
        return text_input
