import pytest
import os
from unittest.mock import patch, MagicMock

from backend.security.auth import verify_password, get_password_hash, create_access_token, decode_access_token
from backend.security.encryption import encrypt_value, decrypt_value
from backend.security.permissions import has_permission, Permission
from backend.security.risk_engine import assess_risk, RiskLevel
from backend.security.guardian import Guardian, SecurityViolation
from backend.security.command_validator import CommandValidator

def test_password_hashing():
    pwd = "supersecretpassword123!"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_lifecycle():
    token = create_access_token({"sub": "admin"})
    decoded = decode_access_token(token)
    assert decoded["sub"] == "admin"

def test_encryption_lifecycle():
    secret_data = "Sensitive Agent Memory Fact"
    encrypted = encrypt_value(secret_data)
    assert encrypted != secret_data
    decrypted = decrypt_value(encrypted)
    assert decrypted == secret_data

def test_rbac_permissions():
    # STARK should be able to execute scripts but not read user memory
    assert has_permission("STARK", Permission.EXECUTE_SCRIPT) is True
    assert has_permission("STARK", Permission.READ_MEMORY) is False
    
    # FURY is system level, can do everything
    assert has_permission("FURY", Permission.SYSTEM_CONTROL) is True
    assert has_permission("FURY", Permission.READ_MEMORY) is True

def test_risk_engine_classification():
    assert assess_risk("execute_script", "rm -rf /") == RiskLevel.CRITICAL
    assert assess_risk("execute_script", "format c:") == RiskLevel.CRITICAL
    assert assess_risk("execute_script", "echo 'hello'") == RiskLevel.LOW
    assert assess_risk("execute_script", "python network_scan.py") == RiskLevel.HIGH

def test_command_validator():
    validator = CommandValidator()
    
    # Valid command
    is_valid, cmd_array = validator.validate("python script.py")
    assert is_valid is True
    assert cmd_array == ["python", "script.py"]
    
    # Shell injection attempts
    is_valid, _ = validator.validate("python script.py ; rm -rf /")
    assert is_valid is False
    
    is_valid, _ = validator.validate("python script.py && echo 'hacked'")
    assert is_valid is False
    
    is_valid, _ = validator.validate("echo $(whoami)")
    assert is_valid is False

@patch("backend.security.guardian.log_security_event")
@patch("backend.security.guardian.ids_monitor")
def test_guardian_kernel_blocking(mock_ids, mock_log):
    guardian = Guardian()
    
    # Blocked due to RBAC
    with pytest.raises(SecurityViolation):
        guardian.authorize_execution("STARK", "read_memory", "user_profile")
        
    # Blocked due to Risk
    with pytest.raises(SecurityViolation):
        guardian.authorize_execution("FURY", "execute_script", "rm -rf /")
        
    # Allowed
    assert guardian.authorize_execution("STARK", "execute_script", "python script.py") is True
