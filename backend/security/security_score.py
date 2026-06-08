from backend.security.intrusion_detection import ids_monitor

class SecurityScoreEngine:
    @staticmethod
    def calculate_overall_security_score() -> dict:
        base_score = 100
        
        failed_auth_count = len(ids_monitor.failed_auth_attempts)
        prompt_injection_count = sum(ids_monitor.prompt_injection_attempts.values())
        agent_violation_count = sum(ids_monitor.agent_violation_counts.values())
        
        penalty = (failed_auth_count * 10) + (prompt_injection_count * 20) + (agent_violation_count * 15)
        score = max(0, base_score - penalty)
        
        status = "SECURE"
        if score <= 50:
            status = "CRITICAL"
        elif score <= 80:
            status = "ELEVATED"
            
        return {
            "threat_score": score,
            "active_blocks": failed_auth_count,
            "prompt_injections": prompt_injection_count,
            "agent_violations": agent_violation_count,
            "status": status
        }

security_engine = SecurityScoreEngine()
