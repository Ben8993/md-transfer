import requests
import json
import os
from datetime import datetime
import logging

# ==== CONFIGURATION ====
JFROG_URL = "https://your.jfrog.instance"
USERNAME = "youruser"
PASSWORD = "yourpass"
TARGET_COMPONENT = "generic://libs-release-local/com/example/app/1.0.0/app-1.0.0.jar"
WATCH_NAME = "prod-policy"  # Only include violations from this watch
OUTPUT_REPO = "reports-local"
AUTH = (USERNAME, PASSWORD)
REPORT_FILENAME = f"critical_cves_{WATCH_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
MITIGATED_CVES_FILE = "mitigated_cves.txt"
LOG_FILE = "script.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Script started.")

# ==== Load Mitigated CVEs ====
# This file should contain one CVE ID per line
def load_mitigated_cves():
    try:
        with open(MITIGATED_CVES_FILE, "r") as f:
            logging.info(f"Loaded mitigated CVEs from {MITIGATED_CVES_FILE}")
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        logging.warning("Mitigated CVEs file not found. Continuing without it.")
        print("⚠️ Mitigated CVEs file not found. Continuing without it.")
        return set()

# ==== STEP 1: Get Violations for Component ====
def get_component_violations():
    url = f"{JFROG_URL}/xray/api/v1/violations"
    logging.info(f"Fetching violations from {url}")
    payload = {
        "filters": {
            "severities": ["Critical"],
            "violation_type": "security"
        },
        "pagination": {
            "order_by": "severity",
            "limit": 100
        }
    }

    response = requests.post(url, auth=AUTH, json=payload)
    response.raise_for_status()
    logging.info("Violations fetched successfully.")
    return response.json()

# ==== STEP 2: Filter by Component and Watch ====
def filter_violations(data):
    cves = {}
    for v in data.get("data", []):
        artifact = v.get("impacted_artifact", {}).get("component_id")
        if artifact != TARGET_COMPONENT:
            continue
        if v.get("watch_name") != WATCH_NAME:
            continue
        for issue in v.get("issues", []):
            cve = issue.get("cve", issue.get("issue_id"))
            if not cve:
                continue
            if cve not in cves:
                cves[cve] = {
                    "watch": WATCH_NAME,
                    "artifact": artifact,
                    "cve_id": cve,
                    "summary": issue.get("summary"),
                    "severity": issue.get("severity"),
                    "provider": issue.get("provider"),
                    "impact_path": v.get("impact_path", []),
                    "fixed_versions": issue.get("fixed_versions", []),
                }
    return list(cves.values())

# ==== STEP 3: Write Report ====
def write_json_report(entries):
    with open(REPORT_FILENAME, "w") as f:
        json.dump(entries, f, indent=2)
    logging.info(f"JSON report written to {REPORT_FILENAME}")

# ==== STEP 4: Write Markdown Report ====
def write_markdown_report(entries, mitigated_set):
    md_file = REPORT_FILENAME.replace(".json", ".md")
    with open(md_file, "w") as f:
        f.write(f"# Critical CVEs from Watch: `{WATCH_NAME}`\n\n")
        f.write(f"**Artifact:** `{TARGET_COMPONENT}`\n\n")
        f.write("| CVE ID | Summary | Severity | Fixed Versions | Provider | Platform Mitigated? |\n")
        f.write("|--------|---------|----------|----------------|----------|----------------------|\n")

        for entry in entries:
            cve = entry["cve_id"]
            summary = entry.get("summary", "").replace("\n", " ").strip()
            severity = entry.get("severity", "Unknown")
            fixed_versions = ", ".join(entry.get("fixed_versions", [])) or "N/A"
            provider = entry.get("provider", "N/A")
            mitigated = "Yes" if cve in mitigated_set else "No"

            f.write(f"| `{cve}` | {summary} | {severity} | {fixed_versions} | {provider} | {mitigated} |\n")
    
    logging.info(f"Markdown report written to {md_file}")
    return md_file

# ==== STEP 5: Upload Report ====
def upload_file(file_path):
    file_name = os.path.basename(file_path)
    url = f"{JFROG_URL}/artifactory/{OUTPUT_REPO}/{file_name}"
    logging.info(f"Uploading {file_path} to {url}")
    with open(file_path, "rb") as f:
        response = requests.put(url, auth=AUTH, data=f)
        response.raise_for_status()
        logging.info(f"Uploaded {file_path} to {url}")

# ==== MAIN ====
try:
    logging.info("Loading mitigated CVEs...")
    mitigated_set = load_mitigated_cves()

    # Step 1: Fetch violations
    logging.info("Fetching all critical security violations...")
    print("🔍 Fetching all critical security violations...")
    violations_data = get_component_violations()

    # Step 2: Filter violations
    logging.info("Filtering violations...")
    filtered = filter_violations(violations_data)
    logging.info(f"Found {len(filtered)} CVEs from watch '{WATCH_NAME}'")
    print(f"📋 Found {len(filtered)} CVEs from watch '{WATCH_NAME}'")

    # Step 3: Write reports
    logging.info("Writing reports...")
    write_json_report(filtered)
    md_file = write_markdown_report(filtered, mitigated_set)

    # Step 4: Upload reports
    logging.info("Uploading reports...")
    upload_file(REPORT_FILENAME)
    upload_file(md_file)

    logging.info("Script completed successfully.")

except requests.exceptions.RequestException as req_err:
    logging.error(f"Request error: {req_err}")
    print(f"❌ Request error: {req_err}")
except Exception as e:
    logging.error(f"Error: {e}")
    print(f"❌ Error: {e}")