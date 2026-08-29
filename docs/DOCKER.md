# Docker Deployment Guide for SilentSignal

This guide covers building, running, testing, and managing **SilentSignal** using Docker and Docker Compose.

---

## 1. Quick Start

### Using Docker Compose (Recommended)

From the project root (`SilentSignal_Full_Project/`) or workspace root:

```bash
# Build and run in detached mode
docker compose up --build -d
```

Once started, open [http://localhost:8501](http://localhost:8501) in your browser.

To stop the container:
```bash
docker compose down
```

### Using Convenience Scripts

- **Windows (PowerShell):**
  ```powershell
  .\run_docker.ps1
  ```
- **Linux / macOS:**
  ```bash
  chmod +x run_docker.sh
  ./run_docker.sh
  ```

---

## 2. Using Docker CLI Directly

### Build Image

```bash
docker build -t silentsignal:latest .
```

### Run Container

```bash
docker run -d \
  --name silentsignal-app \
  -p 8501:8501 \
  -v "$(pwd)/artifacts:/app/artifacts" \
  -v "$(pwd)/data:/app/data" \
  silentsignal:latest
```

### View Logs

```bash
docker logs -f silentsignal-app
```

### Stop and Remove Container

```bash
docker stop silentsignal-app
docker rm silentsignal-app
```

---

## 3. Running Unit and Scenario Tests in Docker

Run all tests in the exact containerized Python 3.11 environment:

### Using Docker Compose Profile

```bash
docker compose run --rm silentsignal-test
```

### Using Direct Docker Run

```bash
docker run --rm silentsignal:latest python -m unittest discover -s tests -v
```

---

## 4. Regenerating Demo Data or Running Scripts

You can execute any helper or generator script directly inside the container:

```bash
# Regenerate synthetic demo data
docker run --rm silentsignal:latest python scripts/generate_demo.py

# Re-initialize SQLite audit database
docker run --rm silentsignal:latest python scripts/init_database.py

# Run validation checks
docker run --rm silentsignal:latest python scripts/validate_project.py
```

---

## 5. Architecture & Container Details

- **Base Image:** `python:3.11-slim`
- **Exposed Port:** `8501` (Streamlit web dashboard)
- **User:** Non-root `appuser` (UID: 1000) for enhanced security
- **Healthcheck:** Automatic polling on `http://localhost:8501/_stcore/health`
- **Persistence:** Volume mounts `./artifacts` and `./data` ensure that audit events, feedback, runtime benchmarks, and data caches survive container restarts.
- **Cold-Start Automation:** `docker-entrypoint.sh` automatically checks for raw data and audit database existence, automatically generating them on first run if missing.
