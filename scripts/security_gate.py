"""Apply the SecureGuard deployment policy to CI scanner evidence."""

import json
import os
import sys
from collections import Counter
from pathlib import Path


def read_json(path: str, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


semgrep = read_json("semgrep-results.json", {"results": []})
audit = read_json("pip-audit-results.json", {"dependencies": []})
trivy = read_json("trivy-results.json", {"Results": []})
counts = Counter()

# A Semgrep ERROR is treated as high risk; a detected committed secret is critical.
counts["HIGH"] += sum(1 for result in semgrep.get("results", []) if result.get("extra", {}).get("severity") == "ERROR")
if os.getenv("GITLEAKS_OUTCOME") == "failure":
    counts["CRITICAL"] += 1

# pip-audit advisories do not always publish CVSS severities. Treat known CVEs
# conservatively as high until a project-specific severity source is introduced.
counts["HIGH"] += sum(len(item.get("vulns", [])) for item in audit.get("dependencies", []))
for result in trivy.get("Results", []):
    for vulnerability in result.get("Vulnerabilities") or []:
        counts[vulnerability.get("Severity", "UNKNOWN").upper()] += 1

blocked = counts["CRITICAL"] >= 1 or counts["HIGH"] >= 5
decision = "BLOCK DEPLOYMENT" if blocked else "ALLOW DEPLOYMENT"
payload = {"decision": decision, "counts": dict(counts), "thresholds": {"critical": 1, "high": 5}}
Path("security-gate.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Risk engine: Critical={counts['CRITICAL']} High={counts['HIGH']} -> {decision}")
sys.exit(1 if blocked else 0)
