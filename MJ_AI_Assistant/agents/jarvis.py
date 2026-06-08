import psutil
from agents.base import BaseAgent
from core.bus import Task

class JarvisAgent(BaseAgent):
    async def handle_task(self, task: Task) -> str:
        """
        Monitors host machine system resources and Ollama endpoints to build comprehensive diagnostic audits.
        """
        await self.emit_log("Conducting machine telemetry collection...")
        
        # 1. Capture system stats
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        ram_used_gb = ram.used / (1024 ** 3)
        ram_total_gb = ram.total / (1024 ** 3)
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)

        # 2. Check Ollama API Status
        ollama_online = self.client.is_online()
        ollama_status = "ONLINE" if ollama_online else "OFFLINE"
        models = self.client.list_local_models() if ollama_online else []

        # 3. Compile report
        diagnostic_report = (
            f"### [JARVIS] System Diagnostic Audit\n"
            f"- **System Telemetry**: CPU: {cpu_usage:.1f}% | RAM: {ram_used_gb:.1f}GB / {ram_total_gb:.1f}GB ({ram.percent}%) | Disk: {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB ({disk.percent}%)\n"
            f"- **Ollama Server**: {ollama_status}\n"
            f"- **Locally Available Models**: {', '.join(models) if models else 'None detected'}\n"
            f"- **Health Status**: {'ALL SYSTEMS OPERATIONAL ✓' if (cpu_usage < 85 and ram.percent < 90 and ollama_online) else 'SYSTEM WARNING: HIGH RESOURCE LOAD OR OLLAMA OFFLINE ✗'}"
        )
        
        await self.emit_log(f"Diagnostics complete: CPU at {cpu_usage:.1f}%")
        return diagnostic_report
