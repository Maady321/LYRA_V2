from typing import Dict, Any
import asyncio
from backend.security.permissions import has_permission, Permission
from backend.security.risk_engine import assess_risk, RiskLevel
from backend.security.audit_logger import log_security_event
from backend.security.intrusion_detection import ids_monitor
import logging

logger = logging.getLogger("GuardianSecurityKernel")

class SecurityViolation(Exception):
    pass

class Guardian:
    """
    The Zero-Trust Security Kernel. 
    Intercepts all execution paths and enforces RBAC and Risk Assessment.
    """
    
    @staticmethod
    def authorize_execution(agent_name: str, action: str, target: str, payload: str = "") -> bool:
        """
        Main entrypoint for checking if an agent can execute a specific action.
        """
        # 1. Map action string to Permission Enum
        required_permission = Guardian._map_action_to_permission(action)
        
        def _safe_audit(level, result_msg):
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(log_security_event("system", agent_name, action, target, level, result_msg))
            except RuntimeError:
                # If called from sync context, we'll log it directly via standard logger for now
                # In production, we could spin up a background thread.
                logger.info(f"[SYNC AUDIT] {agent_name} -> {action} | {level} | {result_msg}")

        # 2. RBAC Check
        if required_permission:
            if not has_permission(agent_name, required_permission):
                err_msg = f"Agent '{agent_name}' lacks permission '{required_permission.name}' to execute '{action}'."
                logger.warning(f"[GUARDIAN BLOCK] {err_msg}")
                ids_monitor.record_agent_violation(agent_name, action)
                _safe_audit("CRITICAL", "BLOCKED - RBAC Violation")
                raise SecurityViolation(err_msg)

        # 3. Risk Engine Check
        risk = assess_risk(action, f"{target} {payload}")
        
        if risk == RiskLevel.CRITICAL:
            err_msg = f"Action '{action}' on '{target}' is classified as CRITICAL risk and is blocked."
            logger.error(f"[GUARDIAN BLOCK] {err_msg}")
            ids_monitor.record_agent_violation(agent_name, f"CRITICAL_RISK_{action}")
            _safe_audit(risk.value, "BLOCKED - Risk Too High")
            raise SecurityViolation(err_msg)
            
        elif risk == RiskLevel.HIGH:
            logger.warning(f"[GUARDIAN ALERT] HIGH RISK Execution approved for {agent_name}: {action} {target}")
            _safe_audit(risk.value, "ALLOWED - High Risk")
        else:
            _safe_audit(risk.value, "ALLOWED")
        
        # If it passes, log and allow.
        logger.info(f"[GUARDIAN ALLOW] {agent_name} -> {action} {target}")
        return True

    @staticmethod
    def _map_action_to_permission(action: str) -> Permission:
        action_lower = action.lower()
        if "read_memory" in action_lower:
            return Permission.READ_MEMORY
        elif "write_memory" in action_lower or "store" in action_lower:
            return Permission.WRITE_MEMORY
        elif "execute" in action_lower or "run_command" in action_lower:
            return Permission.EXECUTE_SCRIPT
        elif "read_file" in action_lower:
            return Permission.READ_FILE
        elif "write_file" in action_lower or "create_file" in action_lower:
            return Permission.WRITE_FILE
        elif "browser" in action_lower or "navigate" in action_lower or "search" in action_lower:
            return Permission.BROWSER_ACCESS
        elif "voice" in action_lower:
            return Permission.VOICE_ACCESS
        # Default fallback, require SYSTEM_CONTROL for unknown actions as a fail-safe
        return Permission.SYSTEM_CONTROL

guardian_kernel = Guardian()
