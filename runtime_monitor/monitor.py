"""Read Docker process metadata and send it to the local threat engine.

This tool only observes `docker top`; it does not execute commands in a
container. Docker Desktop or Docker Engine must be running.
"""

import argparse
import json
import re
import subprocess

from .threat_engine import RuntimeEvent, classify

SAFE_CONTAINER_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
EXPECTED_PROCESSES = {"python", "python3", "flask", "gunicorn"}


def collect_process_events(container: str) -> list[RuntimeEvent]:
    if not SAFE_CONTAINER_NAME.fullmatch(container):
        raise ValueError("Container name contains unsupported characters")
    completed = subprocess.run(
        ["docker", "top", container, "-eo", "pid,ppid,comm,args"],
        check=True, capture_output=True, text=True,
    )
    lines = completed.stdout.splitlines()[1:]
    processes = []
    for line in lines:
        fields = line.split(maxsplit=3)
        if len(fields) >= 3:
            processes.append({"pid": fields[0], "ppid": fields[1], "process": fields[2]})
    names = {item["pid"]: item["process"] for item in processes}
    return [
        RuntimeEvent("process", container, {"process": item["process"], "parent": names.get(item["ppid"], "unknown")})
        for item in processes if item["process"] not in EXPECTED_PROCESSES
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Observe Docker processes for SecureGuard training.")
    parser.add_argument("--container", required=True, help="Docker container name or ID")
    args = parser.parse_args()
    alerts = classify(collect_process_events(args.container))
    print(json.dumps([alert.__dict__ for alert in alerts], indent=2))


if __name__ == "__main__":
    main()
