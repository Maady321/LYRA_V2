import os
import subprocess
import sqlite3
from pathlib import Path
import sys
# Add Lyra to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.security.guardian import guardian_kernel
from agents.base import BaseAgent
from core.bus import Task

class GhostAgent(BaseAgent):
    def _log_audit(self, action_type: str, target: str, command: str, approved: int, verdict: str) -> None:
        """
        Logs OS transactions securely in the database for tracking.
        """
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                conn.execute(
                    """INSERT INTO computer_control_audit 
                       (action_type, target, command_str, approved_by_user, security_verdict) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (action_type, target, command, approved, verdict)
                )
                conn.commit()
        except Exception as e:
            print(f"[GHOST] Audit logging failure: {e}")

    async def handle_task(self, task: Task) -> str:
        """
        Executes native operating system computer commands, app controls, and file management.
        """
        prompt = task.payload.get("prompt", "").lower().strip()
        await self.emit_log(f"GHOST analyzing OS command intention: '{prompt}'")

        # 1. Open Applications
        if "open" in prompt or "launch" in prompt:
            target_app = ""
            for app in ["notepad", "calc", "explorer", "chrome"]:
                if app in prompt:
                    target_app = app
                    break

            if target_app:
                await self.emit_log(f"Attempting to boot application: {target_app}")
                # Registry confirmation check
                if target_app == "cmd" or target_app == "powershell":
                    # Dangerous app, require explicit approval
                    self._log_audit("APP_LAUNCH", target_app, target_app, 0, "BLOCKED")
                    return f"Permission Denied: GHOST blocked launching dangerous terminal '{target_app}'."

                try:
                    guardian_kernel.authorize_execution("GhostAgent", "run_command", target_app)
                    os.startfile(target_app)
                    self._log_audit("APP_LAUNCH", target_app, f"os.startfile({target_app})", 1, "PASSED")
                    return f"Success: GHOST launched system application '{target_app}'."
                except Exception as e:
                    self._log_audit("APP_LAUNCH", target_app, f"os.startfile({target_app})", 0, f"FAILED: {e}")
                    return f"Error: Failed to launch '{target_app}': {e}"

        # 2. File and Directory Management
        if "folder" in prompt or "directory" in prompt or "file" in prompt:
            # Create a folder
            if "create" in prompt or "make" in prompt:
                import re
                name_match = re.search(r"(?:folder|directory)\s+named\s+(\w+)", prompt)
                folder_name = name_match.group(1) if name_match else "new_folder"
                
                safe_dir = Path(__file__).parent.parent / "scratch"
                safe_dir.mkdir(exist_ok=True)
                new_folder_path = safe_dir / folder_name
                
                try:
                    guardian_kernel.authorize_execution("GhostAgent", "write_file", str(new_folder_path))
                    new_folder_path.mkdir(exist_ok=True)
                    self._log_audit("FILE_CREATE", str(new_folder_path), "mkdir", 1, "PASSED")
                    return f"Success: GHOST created sandboxed folder '{folder_name}' at: {new_folder_path.name}"
                except Exception as e:
                    return f"Error: GHOST failed to create folder: {e}"

        # Default fallback
        self._log_audit("CMD_EXECUTE", "unknown", prompt, 0, "BLOCKED")
        return "GHOST Restriction: Operating system command is unapproved or contains unrecognized safe patterns."
