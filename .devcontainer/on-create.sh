#!/usr/bin/env bash
# .devcontainer/on-create.sh
# Post-create setup for GitHub Codespaces + cloud agent environments.
# Installs all Python and Node deps so the workspace is fully functional on first open.
set -euo pipefail

echo "[INFO] ACA devcontainer on-create starting"

# ---------------------------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------------------------
echo "[INFO] Installing Python service requirements"
pip install --upgrade pip --quiet
pip install -r services/api/requirements.txt --quiet
pip install -r services/collector/requirements.txt --quiet
pip install -r services/analysis/requirements.txt --quiet
pip install -r services/delivery/requirements.txt --quiet

echo "[INFO] Python deps installed"

# ---------------------------------------------------------------------------
# Frontend dependencies
# ---------------------------------------------------------------------------
if [ -d "frontend" ]; then
    echo "[INFO] Installing frontend (npm ci)"
    cd frontend
    npm ci --silent
    cd ..
fi

# ---------------------------------------------------------------------------
# Dev tooling
# ---------------------------------------------------------------------------
pip install ruff mypy pytest --quiet
echo "[INFO] Dev tooling installed: ruff, mypy, pytest"

# ---------------------------------------------------------------------------
# Smoke test: import API app (catches missing dep early)
# ---------------------------------------------------------------------------
echo "[INFO] Smoke test: importing API app"
PYTHONPATH=services/api python -c "from app.main import app; print('[PASS] API app import OK')"

echo "[INFO] ACA devcontainer on-create complete"
echo "[INFO] Run the API:     PYTHONPATH=services/api uvicorn app.main:app --reload --port 8080"
echo "[INFO] Run the frontend: cd frontend && npm run dev"
echo "[INFO] Run tests:         pytest services/ -x -q"
