"""Dashboard data for the local SecureGuard training interface."""

from datetime import datetime, timezone


def dashboard_snapshot() -> dict:
    """Return explicitly labelled training data for the dashboard.

    CI can later upload its JSON reports to replace these local demonstration
    values. No production monitoring claim is made by this endpoint.
    """
    return {
        "mode": "training / simulated response",
        "updated_at": datetime.now(timezone.utc).strftime("%H:%M UTC"),
        "pipeline": {"builds": 1, "failed": 1, "status": "BLOCKED"},
        "security": {"critical": 1, "high": 1, "medium": 0, "low": 0},
        "runtime": {"alerts": 1, "blocked": 1, "response": "SIMULATED"},
        "events": [
            {"time": "now", "risk": "HIGH", "title": "Suspicious process", "detail": "bash spawned by python", "action": "ISOLATE_CONTAINER (SIMULATED)"},
            {"time": "CI", "risk": "CRITICAL", "title": "Secret detected", "detail": "Fake training API key", "action": "BLOCK DEPLOYMENT"},
            {"time": "CI", "risk": "HIGH", "title": "SAST finding", "detail": "Unsafe eval() endpoint", "action": "BLOCK DEPLOYMENT"},
        ],
    }
