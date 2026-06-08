import sys
import os
import re
from pathlib import Path

def update_file(filepath: str, old_pattern: str, new_pattern: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(old_pattern, new_pattern, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated {filepath}")

def switch_to_fake():
    # Update backend/core/config.py
    config_py = r"backend\core\config.py"
    update_file(config_py, r'"lyra\.db"', r'"lyra_fake.db"')
    update_file(config_py, r'"mj_assistant\.db"', r'"mj_assistant_fake.db"')
    
    # Update MJ_AI_Assistant/config/settings.py
    settings_py = r"MJ_AI_Assistant\config\settings.py"
    update_file(settings_py, r'"mj_assistant\.db"', r'"mj_assistant_fake.db"')
    print("Successfully switched to FAKE databases (lyra_fake.db, mj_assistant_fake.db)")

def switch_to_real():
    # Update backend/core/config.py
    config_py = r"backend\core\config.py"
    update_file(config_py, r'"lyra_fake\.db"', r'"lyra.db"')
    update_file(config_py, r'"mj_assistant_fake\.db"', r'"mj_assistant.db"')
    
    # Update MJ_AI_Assistant/config/settings.py
    settings_py = r"MJ_AI_Assistant\config\settings.py"
    update_file(settings_py, r'"mj_assistant_fake\.db"', r'"mj_assistant.db"')
    print("Successfully switched to REAL production databases (lyra.db, mj_assistant.db)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python switch_database.py [fake|real]")
        sys.exit(1)
        
    mode = sys.argv[1].lower()
    if mode == "fake":
        switch_to_fake()
    elif mode == "real":
        switch_to_real()
    else:
        print("Invalid mode. Use 'fake' or 'real'.")
