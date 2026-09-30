# SecureGuard

SecureGuard is a deliberately vulnerable Flask application for a B.Tech DevSecOps project. It provides small, testable examples for CI/CD, SAST, dependency scanning (SCA), container scanning, Docker, and GitHub Actions exercises.

> Warning: This is an educational target only. Do not deploy it to the internet, use real credentials, or reuse its code in a production application.

## Features

- JSON registration and login endpoints
- User profile lookup
- File upload endpoint
- User-list API and demo admin page
- Pytest smoke tests
- Docker image definition

## Intentional vulnerabilities

The code labels every learning target with `VULNERABILITY:` so findings are easy to explain in a report:

- Hard-coded Flask secret
- Plaintext password storage
- SQL injection in login
- Broken access control / IDOR
- Unsafe file-upload handling
- Sensitive-data exposure through API and diagnostics routes

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app app.app run --debug
```

Open `http://127.0.0.1:5000/`. Run tests with:

```powershell
pytest
```

## Run with Docker

```powershell
docker build -t secureguard .
docker run --rm -p 5000:5000 secureguard
```

## Suggested DevSecOps pipeline stages

1. Run `pytest` for basic quality gates.
2. Run SAST (for example, Bandit or Semgrep) to detect code issues.
3. Run SCA (for example, pip-audit) to inspect Python dependencies.
4. Build the Docker image and scan it (for example, Trivy).
5. Publish results in GitHub Actions and create remediation tickets.

The next project phase should add a `.github/workflows/security.yml` pipeline and then remediate each documented issue on a separate branch.
