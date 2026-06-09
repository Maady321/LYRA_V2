import os
import ast
import json
import glob
from collections import defaultdict

# Paths to scan
TARGET_DIRS = [
    r"c:\sabari\Lyra\backend",
    r"c:\sabari\Lyra\MJ_AI_Assistant"
]

# Patterns to look for
SINK_PATTERNS = {
    'subprocess.run': 'OS Execution',
    'subprocess.Popen': 'OS Execution',
    'os.system': 'OS Execution',
    'os.startfile': 'OS Execution',
    'os.remove': 'File Deletion',
    'shutil.rmtree': 'Directory Deletion',
    'webbrowser.open': 'Browser Execution',
    'sqlite3.connect': 'Direct DB Access',
    'open': 'File Access',  # Sometimes builtin open is too noisy, we'll see
}

class GuardianAuditVisitor(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.findings = []
        self.current_function = None
        self.current_function_has_guardian = False
        self.is_api_route = False
        
    def visit_FunctionDef(self, node):
        prev_func = self.current_function
        prev_has_guardian = self.current_function_has_guardian
        prev_is_api_route = self.is_api_route
        
        self.current_function = node.name
        self.current_function_has_guardian = False
        self.is_api_route = False
        
        # Check if it's an API route
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr in ('get', 'post', 'put', 'delete', 'patch'):
                    self.is_api_route = True
                    self.findings.append({
                        'type': 'API Route',
                        'name': node.name,
                        'file': self.filepath,
                        'line': node.lineno,
                        'has_guardian': False # Will be updated if we find it
                    })
        
        self.generic_visit(node)
        
        # Update findings for this function if we found Guardian
        if self.current_function_has_guardian:
            for f in self.findings:
                if f.get('func_name') == node.name and f.get('file') == self.filepath:
                    f['has_guardian'] = True
                if f.get('type') == 'API Route' and f.get('name') == node.name and f.get('file') == self.filepath:
                    f['has_guardian'] = True
                    
        self.current_function = prev_func
        self.current_function_has_guardian = prev_has_guardian
        self.is_api_route = prev_is_api_route
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def visit_Call(self, node):
        # Check if it's a call to guardian_kernel.authorize_execution
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'authorize_execution':
                # Heuristic: if called, Guardian is active in this scope
                self.current_function_has_guardian = True
                
        # Check for sinks
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
                
        if func_name in SINK_PATTERNS:
            self.findings.append({
                'type': 'Execution Sink',
                'sink': func_name,
                'category': SINK_PATTERNS[func_name],
                'func_name': self.current_function or '<module>',
                'file': self.filepath,
                'line': node.lineno,
                'has_guardian': self.current_function_has_guardian # Will be back-patched at end of func
            })
            
        self.generic_visit(node)

def analyze_codebase():
    all_findings = []
    
    for target_dir in TARGET_DIRS:
        for root, _, files in os.walk(target_dir):
            if 'venv' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        tree = ast.parse(content, filename=filepath)
                        visitor = GuardianAuditVisitor(filepath)
                        visitor.visit(tree)
                        all_findings.extend(visitor.findings)
                    except Exception as e:
                        print(f"Error parsing {filepath}: {e}")
                        
    return all_findings

if __name__ == "__main__":
    findings = analyze_codebase()
    with open(r"C:\sabari\Lyra\scratch\audit_results.json", "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)
    print(f"Found {len(findings)} execution paths.")
