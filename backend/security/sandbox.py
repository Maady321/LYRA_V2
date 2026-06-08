import subprocess
import shlex
import os
from backend.core.config import settings

class SandboxViolation(Exception):
    pass

def execute_in_sandbox(command: str, timeout: int = 15) -> str:
    """
    Executes a shell command in a restricted environment.
    Prevents directory traversal out of workspace, strips dangerous env vars,
    and enforces strict timeouts. Now uses CommandValidator to strip shell=True.
    """
    from backend.security.command_validator import validate_command
    
    # 1. Validate and Parse Command into safe arguments
    allowed_command_list, risk_level = validate_command(command)
    
    # 2. Restrict Environment Variables
    safe_env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "PYTHONPATH": settings.BASE_DIR,
        # Strip AWS keys, DB passwords, etc.
    }
    
    # 3. Enforce CWD to be within the safe workspace
    safe_cwd = os.path.join(settings.BASE_DIR, "sandbox_workspace")
    if not os.path.exists(safe_cwd):
        os.makedirs(safe_cwd, exist_ok=True)
        
    try:
        # Strict Shell=False enforcement.
        result = subprocess.run(
            allowed_command_list,
            shell=False,
            check=True,
            cwd=safe_cwd,
            env=safe_env,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        return output
    except subprocess.CalledProcessError as e:
        raise SandboxViolation(f"Execution failed with error code {e.returncode}: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise SandboxViolation(f"Execution exceeded the maximum allowed time of {timeout} seconds.")
    except Exception as e:
        raise SandboxViolation(f"Sandbox execution failed: {str(e)}")
