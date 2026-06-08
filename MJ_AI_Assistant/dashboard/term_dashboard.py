import os
import sys
import time
import asyncio
import psutil
from datetime import datetime
from typing import List, Dict, Any

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live

# Ensure absolute paths resolve correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.orchestrator import MJOrchestrator
from config.settings import settings

console = Console()

class TermDashboard:
    def __init__(self, orchestrator: MJOrchestrator):
        self.orchestrator = orchestrator
        self.start_time = time.time()
        self.activity_logs: List[str] = ["[System] Welcome to MJ AI Assistant. Platforms active."]
        
        # Subscribe dashboard logs listener to monitor channels
        self.orchestrator.bus.subscribe("system_monitor_channel", self._handle_bus_log)
        self.orchestrator.bus.subscribe("notification_channel", self._handle_bus_alert)

    def _handle_bus_log(self, event) -> None:
        log_data = event.data
        agent_name = event.sender
        log_str = f"[{agent_name}] {log_data.get('log', '')}"
        self.activity_logs.append(log_str)
        # Limit history
        if len(self.activity_logs) > 12:
            self.activity_logs.pop(0)

    def _handle_bus_alert(self, event) -> None:
        alert_text = event.data.get("message", "")
        self.activity_logs.append(f"[ALERT] 🔔 {alert_text}")
        if len(self.activity_logs) > 12:
            self.activity_logs.pop(0)

    def _get_uptime(self) -> str:
        elapsed = time.time() - self.start_time
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s"

    def make_header(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        title = Text("MJ AI ASSISTANT OPERATING PLATFORM", style="bold cyan")
        status = Text("SYSTEM STATUS: ONLINE", style="bold green")
        
        grid.add_row(title, status)
        return Panel(grid, style="cyan")

    def make_host_metrics(self) -> Panel:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(ratio=2)
        table.add_column(ratio=8)

        # Build progress visual bars
        def make_bar(val: float, color: str) -> str:
            width = int(val / 10)
            bar = "█" * width + "░" * (10 - width)
            return f"[{color}]{bar}[/{color}] {val}%"

        table.add_row("CPU Load:", make_bar(cpu, "cyan"))
        table.add_row("Memory RAM:", make_bar(ram, "magenta"))
        table.add_row("Disk C:", make_bar(disk, "green"))
        table.add_row("Uptime:", f"[bold white]{self._get_uptime()}[/bold white]")

        return Panel(table, title="System Health Status", border_style="blue")

    def make_agent_metrics(self) -> Panel:
        bus = self.orchestrator.bus
        table = Table(expand=True, box=None, padding=(0, 1))
        table.add_column("Agent", style="bold white")
        table.add_column("Status", justify="right")

        for name, status in bus.active_agents.items():
            if status == "ONLINE":
                status_text = "[bold green]✓ ONLINE[/bold green]"
            elif status == "BUSY":
                status_text = "[bold yellow]⚡ BUSY[/bold yellow]"
            else:
                status_text = "[bold red]✗ OFFLINE[/bold red]"
            table.add_row(name, status_text)

        return Panel(table, title="Agent Status Panel", border_style="blue")

    def make_ollama_panel(self) -> Panel:
        online = self.orchestrator.client.is_online()
        status_str = "[bold green]ONLINE[/bold green]" if online else "[bold red]OFFLINE[/bold red]"
        model = settings.PRIMARY_MODEL
        
        table = Table.grid(expand=True)
        table.add_row(f"Ollama Server: {status_str}")
        table.add_row(f"Active Model:  [bold cyan]{model}[/bold cyan]")
        table.add_row(f"Embedding:     [bold blue]{settings.EMBEDDING_MODEL}[/bold blue]")
        
        return Panel(table, title="Ollama Core Integration", border_style="cyan")

    def make_logs_panel(self) -> Panel:
        logs_text = "\n".join(self.activity_logs)
        return Panel(logs_text, title="Agent Bus Activity Logs", border_style="blue", expand=True)

    def generate_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left_column", ratio=4),
            Layout(name="right_column", ratio=6)
        )

        layout["left_column"].split(
            Layout(name="health", ratio=1),
            Layout(name="ollama", ratio=1)
        )

        layout["right_column"].split(
            Layout(name="agents", ratio=4),
            Layout(name="logs", ratio=6)
        )

        # Update layouts with panel renderers
        layout["header"].update(self.make_header())
        layout["health"].update(self.make_host_metrics())
        layout["ollama"].update(self.make_ollama_panel())
        layout["agents"].update(self.make_agent_metrics())
        layout["logs"].update(self.make_logs_panel())
        layout["footer"].update(Panel("[bold yellow]Prompt box -> [/bold yellow][italic white]Type command and press Enter. Say 'exit' to terminate.[/italic white]"))

        return layout
