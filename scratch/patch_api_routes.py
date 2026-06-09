import json
import os
import re

AUDIT_RESULTS = r"C:\sabari\Lyra\scratch\audit_results.json"

with open(AUDIT_RESULTS, "r", encoding="utf-8") as f:
    findings = json.load(f)

# Filter for API Routes without Guardian
api_bypasses = [f for f in findings if f["type"] == "API Route" and not f["has_guardian"]]
api_bypasses.sort(key=lambda x: (x['file'], -x['line']))

files_to_patch = {}
for f in api_bypasses:
    fpath = f['file']
    if fpath not in files_to_patch:
        files_to_patch[fpath] = []
    files_to_patch[fpath].append(f)

for fpath, items in files_to_patch.items():
    try:
        with open(fpath, "r", encoding="utf-8") as file:
            lines = file.readlines()
            
        for item in items:
            # We want to insert the guardian kernel call right after the function definition
            line_idx = item['line'] - 1
            func_name = item['name']
            
            # Find the actual def line
            while line_idx < len(lines) and not lines[line_idx].lstrip().startswith("def ") and not lines[line_idx].lstrip().startswith("async def "):
                line_idx += 1
                
            if line_idx >= len(lines):
                continue
                
            def_line = lines[line_idx]
            
            # Find the next line (start of function body)
            body_idx = line_idx + 1
            while body_idx < len(lines):
                if lines[body_idx].strip() == "":
                    body_idx += 1
                    continue
                # If it's a docstring, skip over it
                if '"""' in lines[body_idx]:
                    if lines[body_idx].count('"""') == 2:
                        body_idx += 1
                        break
                    else:
                        body_idx += 1
                        while body_idx < len(lines) and '"""' not in lines[body_idx]:
                            body_idx += 1
                        body_idx += 1
                        break
                break
                
            if body_idx >= len(lines):
                continue
                
            # Determine indentation
            body_line = lines[body_idx]
            indent = body_line[:len(body_line) - len(body_line.lstrip())]
            if not indent:
                indent = "    "
            
            # Determine username
            username = '"anonymous"'
            if "current_user" in def_line:
                username = "current_user.get('username', 'anonymous') if isinstance(current_user, dict) else getattr(current_user, 'username', 'anonymous')"
            
            inject = f'{indent}guardian_kernel.authorize_execution(agent_name={username}, action="api_access", target="{func_name}")\n'
            lines.insert(body_idx, inject)
            
        with open(fpath, "w", encoding="utf-8") as file:
            file.writelines(lines)
            
        print(f"Patched API routes in {fpath}")
    except Exception as e:
        print(f"Failed to patch {fpath}: {e}")
