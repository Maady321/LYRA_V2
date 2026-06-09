import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
from MJ_AI_Assistant.security.guardian import guardian_kernel

class SafeCodeRunner:
    @staticmethod
    def execute_python_script(script_path: Path, timeout: float = 12.0) -> Dict[str, Any]:
        """
        Executes a local Python script in a secure sandbox environment and returns stdout/stderr telemetry.
        """
        if not script_path.exists():
            return {
                "success": False,
                "returncode": -1,
                "output": "Script path does not exist.",
                "error": "FileNotFound"
            }

        try:
            # Resolve system python executable path
            venv_python = script_path.parent.parent / "venv" / "Scripts" / "python.exe"
            python_bin = str(venv_python) if venv_python.exists() else sys.executable

            guardian_kernel.authorize_execution(agent_name="code_runner", action="os_execution", target="subprocess")
            process = subprocess.run(
                [python_bin, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            success = process.returncode == 0
            output = process.stdout
            err = process.stderr

            return {
                "success": success,
                "returncode": process.returncode,
                "output": output,
                "error": err
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -2,
                "output": "",
                "error": "TimeoutExpired: Script exceeded processing limits."
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -3,
                "output": "",
                "error": f"Internal execution failure: {e}"
            }
