# Guardian Security Kernel Execution Map & Coverage Report

## 1. Executive Summary
- **Total Execution Paths:** 107
- **Secured by Guardian:** 84
- **Unsecured (Bypasses):** 23
- **Coverage Percentage:** 78.5%

> **Note:** Any execution path bypassing Guardian inherently bypasses RBAC, Audit Logging, and the Risk Assessment Engine, as Guardian acts as the unified chokepoint for these security controls.

## 2. Top 20 Highest-Risk Bypasses
These execution sinks directly interact with the OS, filesystem, or database without Zero-Trust authorization.

| Risk Level | Type | Sink / Category | Function | File | Line |
|---|---|---|---|---|---|
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `setUp` | `test_dreamer.py` | 23 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `test_fallback_triple_extraction` | `test_dreamer.py` | 53 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `test_fallback_triple_extraction` | `test_dreamer.py` | 63 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `setUp` | `test_guardian.py` | 28 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `setUp` | `test_negotiation_and_fts.py` | 37 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `setUp` | `test_negotiation_and_fts.py` | 47 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `test_fts5_trigger_sync` | `test_negotiation_and_fts.py` | 96 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `test_fts5_trigger_sync` | `test_negotiation_and_fts.py` | 106 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `test_metrics_logging` | `test_oracle.py` | 57 |
| CRITICAL | Execution Sink | sqlite3.connect (Direct DB Access) | `setUp` | `test_user_twin.py` | 22 |
| MEDIUM | Execution Sink | open (File Access) | `_get_or_create_key` | `encryption.py` | 20 |
| MEDIUM | Execution Sink | open (File Access) | `_get_or_create_key` | `encryption.py` | 30 |
| MEDIUM | Execution Sink | open (File Access) | `handle_task` | `banner.py` | 33 |
| MEDIUM | Execution Sink | open (File Access) | `scan_and_hot_load` | `plugin_loader.py` | 29 |
| MEDIUM | Execution Sink | open (File Access) | `_initialize_db` | `analytics_db.py` | 24 |
| MEDIUM | Execution Sink | open (File Access) | `_initialize_db` | `sqlite_db.py` | 30 |
| MEDIUM | Execution Sink | open (File Access) | `setUp` | `test_dreamer.py` | 20 |
| MEDIUM | Execution Sink | open (File Access) | `setUp` | `test_guardian.py` | 25 |
| MEDIUM | Execution Sink | open (File Access) | `setUp` | `test_negotiation_and_fts.py` | 34 |
| MEDIUM | Execution Sink | open (File Access) | `setUp` | `test_user_twin.py` | 19 |

## 3. Full Execution Map (Grouped by File)

### `backend\main.py`
- ✅ SECURED [Line 58] API Route: `root`
- ✅ SECURED [Line 67] API Route: `metrics`

### `backend\api\routes.py`
- ✅ SECURED [Line 31] API Route: `login_for_access_token`
- ✅ SECURED [Line 46] API Route: `health_check`
- ✅ SECURED [Line 71] API Route: `list_models`
- ✅ SECURED [Line 89] API Route: `get_conversations`
- ✅ SECURED [Line 105] API Route: `create_conversation`
- ✅ SECURED [Line 120] API Route: `get_conversation`
- ✅ SECURED [Line 135] API Route: `update_conversation`
- ✅ SECURED [Line 154] API Route: `delete_conversation`
- ✅ SECURED [Line 175] API Route: `get_settings`
- ✅ SECURED [Line 183] API Route: `update_setting`
- ✅ SECURED [Line 204] API Route: `list_images`
- ✅ SECURED [Line 255] API Route: `get_image`
- ✅ SECURED [Line 271] API Route: `open_image_natively`
- ✅ SECURED [Line 287] Execution Sink: `os.startfile` inside `open_image_natively()`
- ✅ SECURED [Line 297] API Route: `delete_image`
- ✅ SECURED [Line 313] Execution Sink: `os.remove` inside `delete_image()`
- ✅ SECURED [Line 323] API Route: `get_agents_telemetry`
- ✅ SECURED [Line 343] Execution Sink: `sqlite3.connect` inside `get_agents_telemetry()`
- ✅ SECURED [Line 380] API Route: `get_agent_logs`
- ✅ SECURED [Line 392] Execution Sink: `sqlite3.connect` inside `get_agent_logs()`
- ✅ SECURED [Line 411] API Route: `get_active_tasks`
- ✅ SECURED [Line 423] Execution Sink: `sqlite3.connect` inside `get_active_tasks()`
- ✅ SECURED [Line 443] API Route: `get_knowledge_graph_visualizer`
- ✅ SECURED [Line 456] Execution Sink: `sqlite3.connect` inside `get_knowledge_graph_visualizer()`
- ✅ SECURED [Line 506] API Route: `execute_agent_direct_command`
- ✅ SECURED [Line 536] Execution Sink: `sqlite3.connect` inside `execute_agent_direct_command()`
- ✅ SECURED [Line 567] Execution Sink: `sqlite3.connect` inside `execute_agent_direct_command()`
- ✅ SECURED [Line 613] API Route: `get_morning_briefing`
- ✅ SECURED [Line 631] Execution Sink: `sqlite3.connect` inside `get_morning_briefing()`
- ✅ SECURED [Line 716] API Route: `get_security_logs`
- ✅ SECURED [Line 727] API Route: `get_security_status`
- ✅ SECURED [Line 735] API Route: `get_security_logs`

### `backend\api\routers\governance.py`
- ✅ SECURED [Line 19] API Route: `onboard_agent`
- ✅ SECURED [Line 43] API Route: `certify_agent`
- ✅ SECURED [Line 64] API Route: `deprecate_agent`
- ✅ SECURED [Line 76] API Route: `search_marketplace`

### `backend\api\routers\mlops.py`
- ✅ SECURED [Line 27] API Route: `create_prompt`
- ✅ SECURED [Line 41] API Route: `initialize_ab_test`
- ✅ SECURED [Line 62] API Route: `rollback_prompt`

### `backend\security\encryption.py`
- ❌ BYPASS [Line 20] Execution Sink: `open` inside `_get_or_create_key()`
- ❌ BYPASS [Line 30] Execution Sink: `open` inside `_get_or_create_key()`

### `backend\security\sandbox.py`
- ✅ SECURED [Line 37] Execution Sink: `subprocess.run` inside `execute_in_sandbox()`

### `backend\tools\task_manager.py`
- ✅ SECURED [Line 172] Execution Sink: `webbrowser.open` inside `_open_chrome()`
- ✅ SECURED [Line 181] Execution Sink: `webbrowser.open` inside `_search_chrome()`
- ✅ SECURED [Line 190] Execution Sink: `webbrowser.open` inside `_play_youtube()`
- ✅ SECURED [Line 198] Execution Sink: `subprocess.run` inside `_open_notepad()`
- ✅ SECURED [Line 206] Execution Sink: `subprocess.run` inside `_open_calculator()`
- ✅ SECURED [Line 214] Execution Sink: `subprocess.run` inside `_open_explorer()`
- ✅ SECURED [Line 235] Execution Sink: `open` inside `_write_in_notepad()`
- ✅ SECURED [Line 240] Execution Sink: `subprocess.run` inside `_write_in_notepad()`
- ✅ SECURED [Line 351] Execution Sink: `open` inside `_create_image()`
- ✅ SECURED [Line 356] Execution Sink: `subprocess.run` inside `_create_image()`

### `MJ_AI_Assistant\agents\banner.py`
- ❌ BYPASS [Line 33] Execution Sink: `open` inside `handle_task()`

### `MJ_AI_Assistant\agents\ghost.py`
- ✅ SECURED [Line 19] Execution Sink: `sqlite3.connect` inside `_log_audit()`
- ✅ SECURED [Line 55] Execution Sink: `os.startfile` inside `handle_task()`

### `MJ_AI_Assistant\agents\stark.py`
- ✅ SECURED [Line 83] Execution Sink: `open` inside `handle_task()`
- ✅ SECURED [Line 96] Execution Sink: `subprocess.run` inside `handle_task()`

### `MJ_AI_Assistant\core\negotiation.py`
- ✅ SECURED [Line 51] Execution Sink: `sqlite3.connect` inside `_handle_negotiation_request()`

### `MJ_AI_Assistant\core\oracle.py`
- ✅ SECURED [Line 18] Execution Sink: `sqlite3.connect` inside `_initialize_oracle_tables()`
- ✅ SECURED [Line 61] Execution Sink: `sqlite3.connect` inside `route_task()`
- ✅ SECURED [Line 92] Execution Sink: `sqlite3.connect` inside `log_metrics()`

### `MJ_AI_Assistant\core\plugin_loader.py`
- ❌ BYPASS [Line 29] Execution Sink: `open` inside `scan_and_hot_load()`

### `MJ_AI_Assistant\memory\analytics_db.py`
- ✅ SECURED [Line 15] Execution Sink: `sqlite3.connect` inside `_get_connection()`
- ❌ BYPASS [Line 24] Execution Sink: `open` inside `_initialize_db()`

### `MJ_AI_Assistant\memory\dreamer.py`
- ✅ SECURED [Line 23] Execution Sink: `sqlite3.connect` inside `consolidate_recent_memories()`

### `MJ_AI_Assistant\memory\goal_manager.py`
- ✅ SECURED [Line 18] Execution Sink: `sqlite3.connect` inside `register_goal()`
- ✅ SECURED [Line 34] Execution Sink: `sqlite3.connect` inside `add_subtask()`
- ✅ SECURED [Line 55] Execution Sink: `sqlite3.connect` inside `get_pending_subtasks()`
- ✅ SECURED [Line 66] Execution Sink: `sqlite3.connect` inside `update_subtask_status()`

### `MJ_AI_Assistant\memory\graph_engine.py`
- ✅ SECURED [Line 20] Execution Sink: `sqlite3.connect` inside `add_entity()`
- ✅ SECURED [Line 44] Execution Sink: `sqlite3.connect` inside `add_relationship()`
- ✅ SECURED [Line 81] Execution Sink: `sqlite3.connect` inside `traverse_multi_hop()`
- ✅ SECURED [Line 100] Execution Sink: `sqlite3.connect` inside `query_semantic_context()`

### `MJ_AI_Assistant\memory\sqlite_db.py`
- ✅ SECURED [Line 17] Execution Sink: `sqlite3.connect` inside `_get_connection()`
- ❌ BYPASS [Line 30] Execution Sink: `open` inside `_initialize_db()`

### `MJ_AI_Assistant\memory\vector_store.py`
- ✅ SECURED [Line 68] Execution Sink: `sqlite3.connect` inside `search_similar_memories()`

### `MJ_AI_Assistant\memory\workspace_manager.py`
- ✅ SECURED [Line 15] Execution Sink: `sqlite3.connect` inside `create_note()`
- ✅ SECURED [Line 29] Execution Sink: `sqlite3.connect` inside `search_notes_full_text()`
- ✅ SECURED [Line 38] Execution Sink: `sqlite3.connect` inside `create_project()`
- ✅ SECURED [Line 49] Execution Sink: `sqlite3.connect` inside `list_active_projects()`

### `MJ_AI_Assistant\security\guardian.py`
- ✅ SECURED [Line 33] Execution Sink: `sqlite3.connect` inside `_initialize_default_rules()`
- ✅ SECURED [Line 92] Execution Sink: `sqlite3.connect` inside `validate_action()`
- ✅ SECURED [Line 130] Execution Sink: `sqlite3.connect` inside `log_security_audit()`

### `MJ_AI_Assistant\tests\test_dreamer.py`
- ❌ BYPASS [Line 20] Execution Sink: `open` inside `setUp()`
- ❌ BYPASS [Line 23] Execution Sink: `sqlite3.connect` inside `setUp()`
- ❌ BYPASS [Line 53] Execution Sink: `sqlite3.connect` inside `test_fallback_triple_extraction()`
- ❌ BYPASS [Line 63] Execution Sink: `sqlite3.connect` inside `test_fallback_triple_extraction()`

### `MJ_AI_Assistant\tests\test_guardian.py`
- ❌ BYPASS [Line 25] Execution Sink: `open` inside `setUp()`
- ❌ BYPASS [Line 28] Execution Sink: `sqlite3.connect` inside `setUp()`

### `MJ_AI_Assistant\tests\test_negotiation_and_fts.py`
- ❌ BYPASS [Line 34] Execution Sink: `open` inside `setUp()`
- ❌ BYPASS [Line 37] Execution Sink: `sqlite3.connect` inside `setUp()`
- ❌ BYPASS [Line 47] Execution Sink: `sqlite3.connect` inside `setUp()`
- ❌ BYPASS [Line 96] Execution Sink: `sqlite3.connect` inside `test_fts5_trigger_sync()`
- ❌ BYPASS [Line 106] Execution Sink: `sqlite3.connect` inside `test_fts5_trigger_sync()`

### `MJ_AI_Assistant\tests\test_oracle.py`
- ❌ BYPASS [Line 57] Execution Sink: `sqlite3.connect` inside `test_metrics_logging()`

### `MJ_AI_Assistant\tests\test_user_twin.py`
- ❌ BYPASS [Line 19] Execution Sink: `open` inside `setUp()`
- ❌ BYPASS [Line 22] Execution Sink: `sqlite3.connect` inside `setUp()`

### `MJ_AI_Assistant\tools\code_runner.py`
- ✅ SECURED [Line 27] Execution Sink: `subprocess.run` inside `execute_python_script()`

### `MJ_AI_Assistant\user_model\twin_engine.py`
- ✅ SECURED [Line 19] Execution Sink: `sqlite3.connect` inside `_initialize_default_profile()`
- ✅ SECURED [Line 59] Execution Sink: `sqlite3.connect` inside `analyze_query_for_twin()`
- ✅ SECURED [Line 97] Execution Sink: `sqlite3.connect` inside `add_project()`
- ✅ SECURED [Line 111] Execution Sink: `sqlite3.connect` inside `serialize_digital_twin()`

### `MJ_AI_Assistant\voice\tts.py`
- ❌ BYPASS [Line 74] Execution Sink: `open` inside `download_file()`
- ❌ BYPASS [Line 81] Execution Sink: `open` inside `download_file()`
- ❌ BYPASS [Line 244] Execution Sink: `open` inside `_run_tts_loop()`
