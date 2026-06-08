import asyncio
from backend.database.connection import async_session
from backend.database.models.security import SecurityAuditLog
from backend.core.logger import logger

async def log_security_event(
    user_name: str,
    agent_name: str,
    action: str,
    target: str,
    risk_level: str,
    result: str,
    ip_address: str = "127.0.0.1"
):
    """
    Asynchronously persists a security audit event to the database without blocking the main execution path.
    """
    try:
        async with async_session() as db:
            audit_record = SecurityAuditLog(
                user_name=user_name,
                agent_name=agent_name,
                action=action,
                target=target,
                risk_level=risk_level,
                result=result,
                ip_address=ip_address
            )
            db.add(audit_record)
            await db.commit()
    except Exception as e:
        logger.error(f"[AUDIT FAIL] Failed to write security log to database: {e}")
