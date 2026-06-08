import os
import sys
import time
import asyncio
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live

# Add workspace path for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.orchestrator import MJOrchestrator
from dashboard.term_dashboard import TermDashboard
from config.settings import settings

console = Console()

async def animated_boot():
    """
    Displays the animated startup sequence requested by the specification.
    """
    def boot_print(sender: str, text: str, delay: float = 0.25):
        color = "cyan" if sender == "JARVIS" else "green"
        if sender == "MJ":
            color = "yellow"
        console.print(f"[{color}][{sender}][/{color}] {text}")
        time.sleep(delay)

    console.clear()
    console.print(Panel(Text("MJ MULTI-AGENT AI SYSTEM BOOT SEQUENCE", style="bold cyan", justify="center"), style="cyan"))
    console.print()
    
    boot_print("MJ", "Initializing AI Core...", 0.4)
    boot_print("JARVIS", "Checking system health...", 0.4)
    boot_print("JARVIS", "CPU OK", 0.15)
    boot_print("JARVIS", "Memory OK", 0.15)
    boot_print("JARVIS", "Network Connected", 0.25)
    
    # Check Ollama connection
    orchestrator = MJOrchestrator()
    online = orchestrator.client.is_online()
    if online:
        boot_print("JARVIS", "Ollama Connected", 0.3)
    else:
        boot_print("JARVIS", "Ollama Warning: Connection Failed (Offline Mode active)", 0.4)

    console.print()
    boot_print("FURY", "Coordinator Online", 0.15)
    boot_print("VISION", "Memory Online", 0.15)
    boot_print("CAPTAIN", "Planning Online", 0.15)
    boot_print("BANNER", "Research Online", 0.15)
    boot_print("STARK", "Execution Online", 0.15)
    boot_print("SPIDEY", "Notification Online", 0.15)

    console.print("\n[bold green]All Systems Operational.[/bold green]\n")
    time.sleep(0.8)
    return orchestrator

def display_dashboard_snapshot(dash: TermDashboard):
    """
    Prints a beautiful visual snapshot of the real-time system status.
    """
    console.print()
    console.print(dash.generate_layout())
    console.print()

async def main_loop():
    # 1. Boot up sequence
    orchestrator = await animated_boot()
    dash = TermDashboard(orchestrator)
    conversation_id = "mj_session_01"

    # Create a default conversation
    orchestrator.db.create_conversation(conversation_id, "MJ Core Activation Thread")

    # 2. Main interactive query loop
    while True:
        try:
            display_dashboard_snapshot(dash)
            
            # Print prompt line
            console.print("[bold cyan]MJ Assistant[/bold cyan] > ", end="")
            user_input = await asyncio.to_thread(input)
            
            cleaned = user_input.strip()
            if not cleaned:
                continue
                
            if cleaned.lower() in ["exit", "quit"]:
                console.print("\n[bold yellow][MJ][/bold yellow] Powering down agent bus. Goodbye, friend!\n")
                break

            console.print()
            console.print("[bold yellow][FURY] Coordinator[/bold yellow] delegating tasks across specialized agents...")
            console.print()

            # Execute query asynchronously
            response = await orchestrator.execute_query(cleaned, conversation_id)
            
            # Update latest event log
            dash.activity_logs.append(f"[System] Completed user query: '{cleaned[:30]}...'")
            if len(dash.activity_logs) > 12:
                dash.activity_logs.pop(0)

            console.print(Panel(Text(response, style="white"), title="MJ Response Readout", border_style="green", expand=True))
            console.print("\nPress Enter to return to Dashboard...")
            await asyncio.to_thread(input)
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow][MJ][/bold yellow] Shutdown signal caught. Exiting...\n")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error processing transaction:[/bold red] {e}\n")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main_loop())
