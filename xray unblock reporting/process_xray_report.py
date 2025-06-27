import json
import os
from datetime import datetime

MITIGATED_FILE = "mitigated_cves.txt"
RAW_INPUT = "raw_violations.json"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_BASENAME = f"xray_critical_cves_{TIMESTAMP}"

def load_mitigated_list():
    try:
        with open(MITIGATED_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def process_violations():
    with open(RAW_INPUT, "r") as f:
        data = json.load(f)

    mitigated = load_mitigated_list()
    result = []

    for v in data.get("data", []):
        component = v.get("impacted_artifact", {}).get("component_id")
        watch = v.get("watch_name")
        for issue in v.get("issues", []):
            cve = issue.get("cve") or issue.get("issue_id")
            result.append({
                "cve_id": cve,
                "summary": issue.get("summary", "").strip(),
                "severity": issue.get("severity", "Unknown"),
                "provider": issue.get("provider", "Unknown"),
                "fixed_versions": issue.get("fixed_versions", []),
                "artifact": component,
                "watch": watch,
                "mitigated": "Yes" if cve in mitigated else "No"
            })
    return result

def write_reports(entries):
    json_file = f"{REPORT_BASENAME}.json"
    md_file = f"{REPORT_BASENAME}.md"

    with open(json_file, "w") as jf:
        json.dump(entries, jf, indent=2)

    with open(md_file, "w") as mf:
        mf.write("# Critical CVEs Report\n\n")
        mf.write("| CVE ID | Summary | Severity | Fixed Versions | Provider | Platform Mitigated? |\n")
        mf.write("|--------|---------|----------|----------------|----------|----------------------|\n")

        for e in entries:
            fixed = ", ".join(e["fixed_versions"]) or "N/A"
            mf.write(f"| `{e['cve_id']}` | {e['summary']} | {e['severity']} | {fixed} | {e['provider']} | {e['mitigated']} |\n")

    return json_file, md_file

if __name__ == "__main__":
    print("🔍 Processing Xray violations...")
    entries = process_violations()
    json_out, md_out = write_reports(entries)
    print(f"✅ Reports generated: {json_out}, {md_out}")
