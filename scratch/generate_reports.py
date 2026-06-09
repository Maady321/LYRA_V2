import json
import os

with open(r"C:\sabari\Lyra\scratch\audit_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

total_paths = len(results)
covered_paths = len([r for r in results if r["has_guardian"]])
bypassed_paths = total_paths - covered_paths
coverage_percent = round((covered_paths / total_paths) * 100, 2) if total_paths else 0

# Sort by risk
# OS Execution > DB Access > File Deletion > File Access > API Route > others
risk_weights = {
    "OS Execution": 100,
    "File Deletion": 90,
    "Direct DB Access": 80,
    "API Route": 60,
    "File Access": 40,
    "Browser Execution": 20
}

bypasses = [r for r in results if not r["has_guardian"]]
for b in bypasses:
    cat = b.get("category", "API Route" if b["type"] == "API Route" else "Unknown")
    b["risk_score"] = risk_weights.get(cat, 10)

bypasses.sort(key=lambda x: x["risk_score"], reverse=True)
top_20 = bypasses[:20]

# Generate guardian_coverage_report.json
report = {
    "total_execution_paths": total_paths,
    "paths_covered_by_guardian": covered_paths,
    "paths_bypassing_guardian": bypassed_paths,
    "paths_bypassing_rbac": bypassed_paths, # Since Guardian handles RBAC
    "paths_bypassing_audit": bypassed_paths, # Since Guardian handles Audit
    "paths_bypassing_risk_engine": bypassed_paths, # Since Guardian handles Risk Assessment
    "coverage_percentage": coverage_percent,
    "top_risk_bypasses": top_20,
    "all_bypasses": bypasses
}

with open(r"C:\sabari\Lyra\guardian_coverage_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

# Generate guardian_execution_map.md
md = [
    "# Guardian Security Kernel Execution Map & Coverage Report",
    "",
    "## 1. Executive Summary",
    f"- **Total Execution Paths:** {total_paths}",
    f"- **Secured by Guardian:** {covered_paths}",
    f"- **Unsecured (Bypasses):** {bypassed_paths}",
    f"- **Coverage Percentage:** {coverage_percent}%",
    "",
    "> **Note:** Any execution path bypassing Guardian inherently bypasses RBAC, Audit Logging, and the Risk Assessment Engine, as Guardian acts as the unified chokepoint for these security controls.",
    "",
    "## 2. Top 20 Highest-Risk Bypasses",
    "These execution sinks directly interact with the OS, filesystem, or database without Zero-Trust authorization.",
    ""
]

md.append("| Risk Level | Type | Sink / Category | Function | File | Line |")
md.append("|---|---|---|---|---|---|")

for b in top_20:
    risk_label = "CRITICAL" if b["risk_score"] >= 80 else ("HIGH" if b["risk_score"] >= 60 else "MEDIUM")
    sink = b.get('sink', 'N/A')
    cat = b.get('category', b['type'])
    fname = os.path.basename(b['file'])
    func_name = b.get('func_name', b.get('name', 'Unknown'))
    md.append(f"| {risk_label} | {b['type']} | {sink} ({cat}) | `{func_name}` | `{fname}` | {b['line']} |")

md.extend([
    "",
    "## 3. Full Execution Map (Grouped by File)",
    ""
])

# Group all by file
grouped = {}
for r in results:
    fpath = r['file']
    if fpath not in grouped:
        grouped[fpath] = []
    grouped[fpath].append(r)

for fpath, items in grouped.items():
    fname = os.path.relpath(fpath, start=r"C:\sabari\Lyra")
    md.append(f"### `{fname}`")
    for item in items:
        status = "✅ SECURED" if item["has_guardian"] else "❌ BYPASS"
        if item["type"] == "API Route":
            md.append(f"- {status} [Line {item['line']}] API Route: `{item['name']}`")
        else:
            md.append(f"- {status} [Line {item['line']}] Execution Sink: `{item['sink']}` inside `{item['func_name']}()`")
    md.append("")

with open(r"C:\sabari\Lyra\guardian_execution_map.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md))
