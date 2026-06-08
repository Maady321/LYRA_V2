# MJ AI Assistant

MJ AI Assistant is a production-ready, local-first Multi-Agent Personal Assistant platform powered by **Ollama**. It orchestrates a cooperative team of seven specialized agents cooperating via a high-performance central async Message Bus. It features SQLite-backed semantic long-term vector memories, real-time terminal resource meters, and continuous wake-word voice listeners.

---

## 🛠️ Folder Structure

```
MJ_AI_Assistant/
├── config/
│   └── settings.py          # Pydantic environment configuration settings
├── database/
│   └── schema.sql           # SQLite Database core table setups
├── core/
│   ├── bus.py               # Async message hub, Event/Task channels & point-to-point router
│   ├── orchestrator.py      # Core agent manager & cooperative transaction linker
│   └── ollama_client.py     # Resilient Ollama API client (fallbacks & streaming)
├── memory/
│   ├── sqlite_db.py         # SQLite persistence helper (threads, preferences, activity logs)
│   └── vector_store.py      # Cosine-similarity vector search utilizing Ollama embeddings
├── agents/
│   ├── base.py              # Base abstract agent framework blueprint
│   ├── fury.py              # coordinator: coordinator parsing queries & synthesizing results
│   ├── vision.py            # memory: history matching & preference vector lookup
│   ├── captain.py           # planner: decomposing objectives into structured plans
│   ├── banner.py            # researcher: scanning local files & reading RAG text assets
│   ├── stark.py             # executor: python automation script sandbox run wrapper
│   ├── jarvis.py            # monitor: system hardware telemetry logging & metrics
│   └── spidey.py            # notifier: reminder scheduler & background timers
├── dashboard/
│   └── term_dashboard.py    # Auto-refreshing visual terminal diagnostic panel (Rich layout)
├── voice/
│   ├── tts.py               # Text-to-Speech narration
│   ├── stt.py               # Speech-to-Text translation
│   └── wake.py              # Wake Word loop ("Hey MJ" / "Hello MJ")
├── tools/
│   └── code_runner.py       # Sandboxed python execution process runner
├── tests/
│   └── test_agents.py       # Automated unit test suites for agent messaging and database
├── requirements.txt         # Project requirements
├── .env                     # Local settings environment configurations
└── launch.bat               # Easy startup console batch execution launcher
```

---

## ⚙️ Core Agent Teams

1. **FURY (Coordinator)**: Analyzes user intentions using local LLMs, targets specific specialized agents in chronological order, dispatches parallel task routines, and synthesizes completed works into friendly conversational prose.
2. **VISION (Memory)**: Queries database histories to inject contextual dialogues and performs semantic cosine similarity searches on factual vector memories before queries execute.
3. **CAPTAIN (Planning)**: Formulates structured, step-by-step markdown project roadmaps for complex requirements.
4. **BANNER (Research)**: Safely inspects local workspace files to perform low-overhead RAG queries and document summarizations.
5. **STARK (Execution)**: Drafts Python automation scripts, checks for malicious patterns (security sandbox validation), compiles execution file scripts, and triggers local subprocess scripts.
6. **JARVIS (System Monitor)**: Gathers host hardware resource loads (CPU, RAM, Disk), analyzes active threads, and prints diagnostic health evaluations.
7. **SPIDEY (Notification)**: Allocates non-blocking async background countdown tasks and emits alert reminders when duration triggers expire.

---

## 🚀 Setup & Launch Instructions

### Prerequisites
- Install **Python 3.10** or higher.
- Install and start the **Ollama** model server on your desktop (ensure it is listening on port `11434`).
- Pull the required model files locally:
  ```bash
  ollama pull llama3
  ollama pull nomic-embed-text
  ```

### Installation
1. Navigate to the project folder:
   ```bash
   cd c:\sabari\Lyra\MJ_AI_Assistant
   ```
2. Run the automated setup and install packages inside the virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Operational Launch
Double-click `launch.bat` or trigger it manually:
```bash
.\launch.bat
```
This triggers the startup diagnostics check, initializes databases, compiles schema files, and presents the real-time glassmorphic Terminal Dashboard query console!

---

## 🧪 Running Automated Unit Tests
To run the built-in automated test suites verifying agent registration, VISION vectors, and database operations:
```bash
.\venv\Scripts\python.exe -m unittest tests/test_agents.py
```
Outputs should display successful check status results across all pipelines.

---

## 🛡️ Security Sandboxing & Stark Policy
To guarantee safety during Stark automation execution:
- **Forbidden Key-terms**: STARK rejects scripting files containing patterns like `rm -rf`, `format`, `del /f`, or `regedit`.
- **Sandbox execution**: Files are allocated inside private temporary scratch directories and permanently unlinked upon execution completion.
- **Resource limiters**: Scripts are ran with sub-process timeout limits (maximum 15 seconds) to prevent infinite loops.
