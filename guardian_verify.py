import json

# Ensure we are using the latest audit results
# To be completely accurate, this script could re-run AST parsing, but since audit_guardian.py
# was just re-run, we can read its output directly for the report.
with open(r"c:\sabari\Lyra\scratch\audit_results.json", "r", encoding="utf-8") as f:
    findings = json.load(f)

# The user asked specifically about "execution sinks"
sinks = [f for f in findings if f["type"] == "Execution Sink"]

total_sinks = len(sinks)
protected_sinks = len([s for s in sinks if s["has_guardian"]])
unprotected_sinks = [s for s in sinks if not s["has_guardian"]]

print("--- GUARDIAN VERIFICATION REPORT ---")
print(f"How many execution sinks exist? {total_sinks}")
print(f"How many are Guardian protected? {protected_sinks}")
print(f"Which remain unprotected? ({len(unprotected_sinks)} total)")

# Group unprotected by file to make it readable
unprotected_by_file = {}
for s in unprotected_sinks:
    fname = s["file"].split("sabari\\Lyra\\")[-1]
    if fname not in unprotected_by_file:
        unprotected_by_file[fname] = []
    unprotected_by_file[fname].append(f"Line {s['line']}: {s['sink']} ({s['category']}) in `{s['func_name']}()`")

for fname, items in unprotected_by_file.items():
    print(f"\n[{fname}]")
    for item in items:
        print(f"  - {item}")
