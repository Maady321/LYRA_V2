import json
import os
import re

AUDIT_RESULTS = r"C:\sabari\Lyra\scratch\audit_results.json"

with open(AUDIT_RESULTS, "r", encoding="utf-8") as f:
    findings = json.load(f)

# Sort descending by line number so we can inject without messing up line numbers
findings.sort(key=lambda x: (x['file'], -x['line']))

# Group by file
files_to_patch = {}
for f in findings:
    if f["has_guardian"]: continue
    fpath = f['file']
    if "test" in fpath.lower() or "venv" in fpath.lower(): continue
    if fpath not in files_to_patch:
        files_to_patch[fpath] = []
    files_to_patch[fpath].append(f)

for fpath, items in files_to_patch.items():
    try:
        with open(fpath, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        is_backend = "backend" in fpath.replace("\\", "/")
        guardian_import = "from backend.security.guardian import guardian_kernel\n" if is_backend else "from MJ_AI_Assistant.security.guardian import guardian_kernel\n"
        
        # Add import if missing
        content = "".join(lines)
        if "guardian_kernel" not in content:
            # Find the last import
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, guardian_import)
            
            # Update line numbers of items by +1 because we inserted a line at top
            for item in items:
                if item['line'] > last_import_idx:
                    # Actually we don't need to update because we are processing bottom-up
                    pass

        # Since we are modifying list bottom-up (reverse sorted by line), we can insert without shifting preceding lines' targets.
        # Wait, the items are sorted descending by original line number, BUT we just inserted an import at the top!
        # So we should add 1 to all item line numbers if we inserted an import.
        if "guardian_kernel" not in content:
            for item in items:
                if item['line'] > last_import_idx:
                    item['line'] += 1

        for item in items:
            line_idx = item['line'] - 1
            if line_idx >= len(lines): continue
            line_str = lines[line_idx]
            indent = line_str[:len(line_str) - len(line_str.lstrip())]
            
            if item['type'] == 'API Route':
                # Skip if already has user injection (basic patch)
                if "Depends(get_current_user)" in content:
                    # We will do API routes manually or using another pass
                    continue
            elif item['type'] == 'Execution Sink':
                sink = item['sink']
                agent_name = os.path.basename(fpath).replace('.py', '')
                if "sqlite3.connect" in sink:
                    inject = f'{indent}guardian_kernel.authorize_execution(agent_name="{agent_name}", action="db_access", target="sqlite3")\n'
                    lines.insert(line_idx, inject)
                elif "subprocess.run" in sink or "os.system" in sink:
                    inject = f'{indent}guardian_kernel.authorize_execution(agent_name="{agent_name}", action="os_execution", target="subprocess")\n'
                    lines.insert(line_idx, inject)
                elif "os.remove" in sink:
                    inject = f'{indent}guardian_kernel.authorize_execution(agent_name="{agent_name}", action="file_delete", target="filesystem")\n'
                    lines.insert(line_idx, inject)
                    
        with open(fpath, "w", encoding="utf-8") as file:
            file.writelines(lines)
            
        print(f"Patched {fpath}")
    except Exception as e:
        print(f"Failed to patch {fpath}: {e}")

