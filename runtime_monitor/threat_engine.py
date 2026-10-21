"""Small, explainable rule-based threat detection engine."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeEvent:
    kind: str
    container: str
    details: dict


@dataclass(frozen=True)
class RuntimeAlert:
    container: str
    event: str
    risk: str
    score: int
    message: str


def classify(events: list[RuntimeEvent]) -> list[RuntimeAlert]:
    """Convert observable runtime events into explainable security alerts."""
    alerts = []
    for event in events:
        if event.kind == "process" and event.details.get("process") in {"bash", "sh", "zsh"}:
            alerts.append(RuntimeAlert(event.container, "Unexpected process", "HIGH", 80,
                f"{event.details['process']} was started by {event.details.get('parent', 'unknown')}"))
        elif event.kind == "file_activity" and event.details.get("count", 0) >= 100 and event.details.get("seconds", 0) <= 5:
            alerts.append(RuntimeAlert(event.container, "Excessive file modification", "HIGH", 85,
                f"{event.details['count']} files changed in {event.details['seconds']} seconds"))
        elif event.kind == "network" and event.details.get("unexpected"):
            alerts.append(RuntimeAlert(event.container, "Unexpected outbound connection", "MEDIUM", 55,
                f"Outbound connection to {event.details.get('destination', 'unknown destination')}"))
    return alerts
