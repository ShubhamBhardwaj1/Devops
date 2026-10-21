"""Write an evidence-based security report to a GitHub Actions summary."""

import json
import os
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
gate = read_json("security-gate.json", {"decision": "NOT EVALUATED", "counts": {}})

sast_count = len(semgrep.get("results", []))
dependency_cves = sum(len(item.get("vulns", [])) for item in audit.get("dependencies", []))
container = Counter()
for result in trivy.get("Results", []):
    for vulnerability in result.get("Vulnerabilities") or []:
        container[vulnerability.get("Severity", "UNKNOWN").upper()] += 1

# This lab has one deliberately fake key. Gitleaks is the authority that
# detects it; the outcome is used only to display the training result.
gitleaks_outcome = os.getenv("GITLEAKS_OUTCOME", "skipped")
secret_count = 1 if gitleaks_outcome == "failure" else 0

report = f"""# SecureGuard security report

| Scan | Findings |
| --- | ---: |
| SAST (Semgrep) | {sast_count} |
| Secrets (Gitleaks) | {secret_count} |
| Dependency CVEs (pip-audit) | {dependency_cves} |
| Container CVEs (Trivy) | {sum(container.values())} |
| DAST (OWASP ZAP) | {os.getenv("ZAP_OUTCOME", "skipped")} |

## Container severity breakdown

| Critical | High | Medium | Low |
| ---: | ---: | ---: | ---: |
| {container['CRITICAL']} | {container['HIGH']} | {container['MEDIUM']} | {container['LOW']} |

## Deployment decision

**{gate['decision']}** - Critical: {gate['counts'].get('CRITICAL', 0)} / High: {gate['counts'].get('HIGH', 0)}

Policy: block at **1 Critical** or **5 High** findings.
"""

summary = os.getenv("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as stream:
        stream.write(report)
else:
    print(report)
