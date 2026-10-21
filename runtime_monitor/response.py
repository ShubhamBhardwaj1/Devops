"""Safe, simulated incident-response planning for the training monitor."""

from dataclasses import dataclass

from .threat_engine import RuntimeAlert


@dataclass(frozen=True)
class ResponsePlan:
    action: str
    status: str
    container: str
    reason: str


def plan_response(alert: RuntimeAlert) -> ResponsePlan:
    """Plan a response without changing any Docker container state."""
    if alert.risk == "HIGH":
        return ResponsePlan(
            action="ISOLATE_CONTAINER",
            status="SIMULATED",
            container=alert.container,
            reason=f"High-risk runtime alert: {alert.event}",
        )
    return ResponsePlan(
        action="ALERT_ONLY",
        status="SIMULATED",
        container=alert.container,
        reason=f"Review required: {alert.event}",
    )
