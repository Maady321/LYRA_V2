import psutil
import os
import sqlite3

def test_telemetry():
    try:
        print("1. Fetching CPU...")
        cpu_usage = psutil.cpu_percent()
        print(f"CPU: {cpu_usage}")
        
        print("2. Fetching RAM...")
        ram = psutil.virtual_memory()
        print(f"RAM: {ram.percent}")
        
        print("3. Fetching Disk...")
        disk = psutil.disk_usage("/")
        print(f"Disk: {disk.percent}")
        
        db_path = "c:\\sabari\\Lyra\\MJ_AI_Assistant\\database\\mj_assistant.db"
        tasks_today = 0
        active_agent = "FURY"
        
        print(f"4. Checking DB exists at: {db_path}...")
        print(f"Exists: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                row = conn.execute("SELECT COUNT(*) as count FROM agent_logs WHERE status = 'SUCCESS'").fetchone()
                if row:
                    tasks_today = row["count"]
                row_act = conn.execute("SELECT agent_name FROM agent_logs ORDER BY timestamp DESC LIMIT 1").fetchone()
                if row_act:
                    active_agent = row_act["agent_name"]
                conn.close()
                print(f"DB Success! Tasks: {tasks_today}, Active Agent: {active_agent}")
            except Exception as e:
                print(f"DB Exception (caught): {e}")

        print("5. Compiling Agents List...")
        agents_list = [
            {"name": "FURY", "role": "Coordinator Agent", "desc": "Main decision maker, parses queries and synthesizes final reports", "status": "ONLINE" if active_agent != "FURY" else "BUSY"},
            {"name": "VISION", "role": "Memory Agent", "desc": "Handles SQLite dialogue persistence and semantic vector stores", "status": "ONLINE" if active_agent != "VISION" else "BUSY"},
            {"name": "CAPTAIN", "role": "Planning Agent", "desc": "Decomposes complex goals into actionable roadmaps", "status": "ONLINE" if active_agent != "CAPTAIN" else "BUSY"},
            {"name": "BANNER", "role": "Research Agent", "desc": "Conducts local RAG scans and summarized research checks", "status": "ONLINE" if active_agent != "BANNER" else "BUSY"},
            {"name": "STARK", "role": "Execution Agent", "desc": "Compiles and executes sandboxed Python automation tasks safely", "status": "ONLINE" if active_agent != "STARK" else "BUSY"},
            {"name": "JARVIS", "role": "System Monitor Agent", "desc": "Monitors machine CPU, RAM, Disk, and Ollama status", "status": "ONLINE" if active_agent != "JARVIS" else "BUSY"},
            {"name": "SPIDEY", "role": "Notification Agent", "desc": "Schedules non-blocking async background timers and alerts", "status": "ONLINE" if active_agent != "SPIDEY" else "BUSY"}
        ]
        
        result = {
            "cpu": cpu_usage,
            "ram": ram.percent,
            "disk": disk.percent,
            "uptime": "Active",
            "tasks_today": tasks_today,
            "active_agent": active_agent,
            "agents": agents_list
        }
        print("SUCCESS! Final output compiled:")
        print(result)
        
    except Exception as e:
        print("FAILED with Exception:")
        import traceback
        traceback.print_exc()

test_telemetry()
