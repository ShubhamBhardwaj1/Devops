"""Fail the CI policy when Trivy finds high or critical image CVEs."""

import json
import sys
from pathlib import Path

report = Path("trivy-results.json")
if not report.exists():
    print("Trivy report is missing; container security policy cannot be evaluated.")
    sys.exit(1)

try:
    data = json.loads(report.read_text(encoding="utf-8"))
except json.JSONDecodeError:
    print("Trivy report is not valid JSON.")
    sys.exit(1)

blocked = []
for result in data.get("Results", []):
    for vulnerability in result.get("Vulnerabilities") or []:
        if vulnerability.get("Severity", "").upper() in {"CRITICAL", "HIGH"}:
            blocked.append(vulnerability.get("VulnerabilityID", "unknown CVE"))

if blocked:
    print(f"Trivy policy failed: {len(blocked)} high/critical finding(s): {', '.join(blocked)}")
    sys.exit(1)

print("Trivy policy passed: no high or critical findings.")
