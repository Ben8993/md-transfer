# pull-target-violations.py

This script fetches critical security violations for a specific component from JFrog Xray, filters them based on a specified watch, and generates a JSON report. The report is then uploaded to a specified Artifactory repository.

## Prerequisites

1. **Python 3.x**: Ensure Python is installed on your system.
2. **Dependencies**: Install the required Python libraries:
   ```bash
   pip install requests
   ```
3. **JFrog Xray Access**: You need valid credentials and access to the JFrog Xray API.
4. **Artifactory Repository**: Ensure the target repository for uploading the report exists.

---

## Configuration

Before running the script, update the following variables in the script:

- `JFROG_URL`: Your JFrog instance URL (e.g., `https://your.jfrog.instance`).
- `USERNAME`: Your JFrog username.
- `PASSWORD`: Your JFrog password or API token.
- `TARGET_COMPONENT`: The component you want to check for violations (e.g., `generic://libs-release-local/com/example/app/1.0.0/app-1.0.0.jar`).
- `WATCH_NAME`: The name of the Xray watch to filter violations (e.g., `prod-policy`).
- `OUTPUT_REPO`: The Artifactory repository where the report will be uploaded.

---

## Usage

1. **Run the Script**:
   Execute the script using Python:
   ```bash
   python pull-target-violations.py
   ```

2. **Output**:
   - If critical CVEs are found:
     - A JSON report is generated in the current directory with a filename like `critical_cves_prod-policy_YYYYMMDD_HHMMSS.json`.
     - The report is uploaded to the specified Artifactory repository.
   - If no critical CVEs are found, the script will notify you.

3. **Logs**:
   The script prints logs to the console, including:
   - The number of CVEs found.
   - The upload status of the report.
   - Any errors encountered during execution.

---

## Example Output

### Console Output
```plaintext
🔍 Fetching all critical security violations...
📋 Found 3 CVEs from watch 'prod-policy'
✅ Uploaded to: https://your.jfrog.instance/artifactory/reports-local/critical_cves_prod-policy_20250626_123456.json
```

### JSON Report
```json
[
  {
    "watch": "prod-policy",
    "artifact": "generic://libs-release-local/com/example/app/1.0.0/app-1.0.0.jar",
    "cve_id": "CVE-2023-12345",
    "summary": "Example vulnerability summary",
    "severity": "Critical",
    "provider": "JFrog",
    "impact_path": ["path/to/impacted/file"],
    "fixed_versions": ["1.0.1"]
  }
]
```

---

## Error Handling

If an error occurs, the script will print an error message to the console. Common issues include:

- Invalid credentials: Ensure `USERNAME` and `PASSWORD` are correct.
- Network issues: Verify connectivity to the JFrog instance.
- Missing dependencies: Ensure `requests` is installed.

---

## Notes

- For large datasets, consider increasing the `pagination.limit` in the `get_component_violations` function.
- Ensure your JFrog instance supports the Xray API version used in the script.
- Use secure methods to store and retrieve credentials (e.g., environment variables or a secrets manager).

---

## Contact

For questions or issues, contact your DevOps team or refer to the JFrog Xray documentation.
