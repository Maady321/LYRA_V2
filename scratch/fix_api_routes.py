import os
import re

files_to_fix = [
    r"c:\sabari\Lyra\backend\api\routes.py",
    r"c:\sabari\Lyra\backend\api\routers\governance.py",
    r"c:\sabari\Lyra\backend\api\routers\mlops.py",
    r"c:\sabari\Lyra\backend\main.py"
]

for fpath in files_to_fix:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find where guardian_kernel.authorize_execution is inside parens and move it to after the colon
    # But wait, it's easier to just remove all of them that were added to API routes,
    # and re-add them correctly.
    
    # Let's remove all lines starting with guardian_kernel.authorize_execution(agent_name="anonymous", action="api_access"
    # Or agent_name=current_user...
    
    lines = content.split('\n')
    new_lines = []
    guardian_lines = []
    
    for i, line in enumerate(lines):
        if "action=\"api_access\"" in line and "guardian_kernel" in line:
            guardian_lines.append(line.strip())
        else:
            new_lines.append(line)
            
    content = '\n'.join(new_lines)
    
    # Now we need to correctly inject them.
    # To find the start of the function body, we match `def func_name(...):`
    # We can use ast to find the line number of the body, then inject.
    import ast
    
    try:
        tree = ast.parse(content)
        # We need to find all functions decorated with @router or @app
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_route = any(
                    (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr in ('get', 'post', 'put', 'delete', 'patch'))
                    or (isinstance(dec, ast.Attribute) and dec.attr in ('get', 'post', 'put', 'delete', 'patch'))
                    for dec in node.decorator_list
                )
                if is_route:
                    # Find body line
                    body_line = node.body[0].lineno - 1
                    # Is there a docstring?
                    if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                        if len(node.body) > 1:
                            body_line = node.body[1].lineno - 1
                        else:
                            # only docstring
                            body_line = node.body[0].lineno # insert after docstring
                            
                    # determine indent
                    indent = "    "
                    if len(new_lines) > body_line:
                        # calculate indent of the first actual statement
                        stmt_line = new_lines[body_line]
                        indent = stmt_line[:len(stmt_line) - len(stmt_line.lstrip())]
                        if not indent:
                            indent = "    "
                    
                    # determine user
                    username = '"anonymous"'
                    for arg in node.args.args + getattr(node.args, 'kwonlyargs', []):
                        if arg.arg == "current_user":
                            username = "current_user.get('username', 'anonymous') if isinstance(current_user, dict) else getattr(current_user, 'username', 'anonymous')"
                            
                    inject = f'{indent}guardian_kernel.authorize_execution(agent_name={username}, action="api_access", target="{node.name}")'
                    # we insert it into new_lines
                    # Need to adjust because we are mutating a list while iterating over AST... 
                    # Actually, AST line numbers are static, if we insert, subsequent line numbers will be wrong.
                    # We can store the injections in a dict {lineno: code} and apply them after.
                    if not hasattr(tree, 'injections'):
                        tree.injections = {}
                    tree.injections[body_line] = inject
                    
        # Apply injections
        if hasattr(tree, 'injections'):
            offset = 0
            # sort by line number
            for lineno in sorted(tree.injections.keys()):
                new_lines.insert(lineno + offset, tree.injections[lineno])
                offset += 1
                
        with open(fpath, "w", encoding="utf-8") as f:
            f.write('\n'.join(new_lines))
            
        print(f"Fixed API routes in {fpath}")
    except Exception as e:
        print(f"Failed to fix {fpath}: {e}")

