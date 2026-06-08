import re
import os
import sqlite3
import time
import subprocess
from pathlib import Path
from agents.base import BaseAgent
from core.bus import Task
from memory.analytics_db import AnalyticsDB

class StarkAgent(BaseAgent):
    def _is_safe_command(self, cmd: str) -> bool:
        """
        Validates the script/command contents against critical security threat patterns.
        """
        # Block malicious commands
        forbidden = [
            r"rm\s+-rf", r"del\s+/f", r"format", r"mkfs", r"fdisk", 
            r"shutdown", r"reboot", r"sys\.exit", r"registry", r"regedit",
            r"shutil\.rmtree"
        ]
        for pattern in forbidden:
            if re.search(pattern, cmd, re.IGNORECASE):
                return False
        return True

    async def handle_task(self, task: Task) -> str:
        """
        Advanced sandboxed code interpreter capable of executing python scripts, data science, CSV, and charts.
        """
        prompt = task.payload.get("prompt", "")
        start_time = time.time()
        
        await self.emit_log(f"STARK Execution sandbox starting transaction: '{prompt}'")

        system_prompt = (
            "You are STARK, the elite Code Interpreter and execution agent of Lyra AIOS.\n"
            "Your task is to write a self-contained, safe Python script that achieves the user's goal.\n"
            "You have advanced capabilities for data science, CSV data analysis, Excel generation, and charting.\n"
            "If the user wants a chart, use matplotlib/pandas to generate it and save it as a PNG file in the workspace 'c:\\sabari\\Lyra\\' directory.\n"
            "Generate ONLY valid Python code inside a markdown block: ```python ... ```\n"
            "Always include extensive print statements to capture telemetry. Keep file operations isolated to the workspace."
        )

        input_data = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Automate this task: '{prompt}'"}
        ]

        raw_script = self.client.generate_chat_response(input_data)
        
        # Extract python code block
        code_block = ""
        try:
            match = re.search(r"```python\s*(.*?)\s*```", raw_script, re.DOTALL | re.IGNORECASE)
            if match:
                code_block = match.group(1).strip()
            else:
                code_block = raw_script.strip()
        except Exception:
            return "STARK execution abort: Could not parse python automation script."

        if not code_block or "error" in code_block.lower():
            return "STARK execution abort: No executable python instructions generated."

        # Safety checking
        if not self._is_safe_command(code_block):
            await self.emit_log("SECURITY LOCK BLOCKED: Malicious cmd script intercepted!", "FAILED")
            return "Security violation: STARK blocked script execution. Contains potentially dangerous operations."

        # Setup sandbox script file
        script_dir = Path(__file__).parent.parent / "scratch"
        script_dir.mkdir(exist_ok=True)
        script_path = script_dir / "mj_sandbox_script.py"

        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code_block)
        except Exception as e:
            return f"Failed to allocate script file in sandbox: {e}"

        # Subprocess Execution
        try:
            venv_python = Path(__file__).parent.parent / "venv" / "Scripts" / "python.exe"
            python_bin = str(venv_python) if venv_python.exists() else "python"

            process = subprocess.run(
                [python_bin, str(script_path)],
                capture_output=True,
                text=True,
                timeout=15.0
            )

            # Cleanup
            if script_path.exists():
                script_path.unlink()

            latency_ms = int((time.time() - start_time) * 1000)
            success = process.returncode == 0
            
            # Log telemetry details in analytics
            analytics = AnalyticsDB()
            analytics.log_performance(
                agent_name=self.name,
                latency_ms=latency_ms,
                success_status=success
            )

            output_summary = f"Execution Output:\n{process.stdout}\n"
            if process.stderr:
                output_summary += f"Compiler Errors/Telemetry:\n{process.stderr}\n"

            await self.emit_log(f"STARK subprocess finished with exit code {process.returncode}")
            return f"Data Science Automation Completed.\n{output_summary}"
        except subprocess.TimeoutExpired:
            if script_path.exists():
                script_path.unlink()
            await self.emit_log("STARK sandboxed timeout: Aborted after 15 seconds.", "FAILED")
            return "Execution Timeout: The script took too long and was safely aborted."
        except Exception as e:
            if script_path.exists():
                script_path.unlink()
            return f"STARK execution error: {e}"
