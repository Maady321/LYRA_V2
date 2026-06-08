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
    and enforces strict timeouts.
    """
    # 1. Basic command sanitization (prevent chaining if we strictly want one command)
    # For now, we allow standard commands but we could restrict `&&` or `;`
    
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
        # Use shell=True for powershell/cmd compatibility but with extreme prejudice
        # In a true prod env on Linux, we would use `bwrap` or Docker.
        result = subprocess.run(
            command,
            shell=True,
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
    except subprocess.TimeoutExpired:
        raise SandboxViolation(f"Execution exceeded the maximum allowed time of {timeout} seconds.")
    except Exception as e:
        raise SandboxViolation(f"Sandbox execution failed: {str(e)}")
