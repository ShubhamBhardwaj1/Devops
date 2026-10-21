from runtime_monitor.threat_engine import RuntimeEvent, classify
from runtime_monitor.response import plan_response


def test_shell_process_is_high_risk():
    alerts = classify([RuntimeEvent("process", "web-app", {"process": "bash", "parent": "python"})])
    assert alerts[0].risk == "HIGH"
    assert alerts[0].event == "Unexpected process"


def test_file_burst_is_high_risk():
    alerts = classify([RuntimeEvent("file_activity", "web-app", {"count": 100, "seconds": 5})])
    assert alerts[0].score == 85


def test_normal_python_process_has_no_alert():
    assert classify([RuntimeEvent("process", "web-app", {"process": "python", "parent": "init"})]) == []


def test_high_risk_response_is_only_simulated():
    alert = classify([RuntimeEvent("process", "web-app", {"process": "bash", "parent": "python"})])[0]
    response = plan_response(alert)
    assert response.action == "ISOLATE_CONTAINER"
    assert response.status == "SIMULATED"
