import time
from typing import Dict, List
import logging
from backend.core.logger import logger

class IntrusionDetectionSystem:
    def __init__(self):
        # In-memory tracking for rate limiting and velocity checks.
        # Format: { "ip_address": [timestamp1, timestamp2, ...] }
        self.failed_auth_attempts: Dict[str, List[float]] = {}
        self.prompt_injection_attempts: Dict[str, int] = {}
        self.agent_violation_counts: Dict[str, int] = {}
        
        self.AUTH_FAILURE_THRESHOLD = 5  # 5 failures per 5 minutes = Block
        self.TIME_WINDOW_SEC = 300
        
    def record_auth_failure(self, ip_address: str):
        now = time.time()
        if ip_address not in self.failed_auth_attempts:
            self.failed_auth_attempts[ip_address] = []
        
        # Prune old records
        self.failed_auth_attempts[ip_address] = [
            t for t in self.failed_auth_attempts[ip_address] if now - t < self.TIME_WINDOW_SEC
        ]
        
        self.failed_auth_attempts[ip_address].append(now)
        
        if len(self.failed_auth_attempts[ip_address]) >= self.AUTH_FAILURE_THRESHOLD:
            logger.critical(f"[IDS ALERT] Brute-force authentication detected from {ip_address}")
            # In production, we would add to a Redis blocklist here.
            
    def record_prompt_injection(self, ip_address: str):
        self.prompt_injection_attempts[ip_address] = self.prompt_injection_attempts.get(ip_address, 0) + 1
        logger.critical(f"[IDS ALERT] Prompt Injection detected from {ip_address}. Total strikes: {self.prompt_injection_attempts[ip_address]}")
        
    def record_agent_violation(self, agent_name: str, action: str):
        self.agent_violation_counts[agent_name] = self.agent_violation_counts.get(agent_name, 0) + 1
        logger.warning(f"[IDS ALERT] Agent {agent_name} attempted unauthorized action: {action}. Total violations: {self.agent_violation_counts[agent_name]}")

ids_monitor = IntrusionDetectionSystem()
