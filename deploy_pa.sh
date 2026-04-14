#!/usr/bin/env bash
set -euo pipefail

# PythonAnywhere deploy helper for this project.
# Usage:
#   ./deploy_pa.sh [branch]
# Examples:
#   ./deploy_pa.sh
#   ./deploy_pa.sh main

BRANCH="${1:-main}"
ENV_NAME="sheetmojo-env"
PROJECT_DIR="$HOME/sheetmojo"

if ! command -v workon >/dev/null 2>&1; then
  echo "Error: 'workon' not found. Open this in a PythonAnywhere Bash console."
  exit 1
fi

cd "$PROJECT_DIR"
workon "$ENV_NAME"

echo "[deploy] Fetching latest changes from origin/$BRANCH"
git fetch origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "[deploy] Installing/updating dependencies"
pip install -r requirements.txt

echo "[deploy] Running migrations"
python manage.py migrate

echo "[deploy] Collecting static files"
python manage.py collectstatic --noinput

echo "[deploy] Running Django checks"
python manage.py check

echo "Done. Reload the web app from the PythonAnywhere Web tab."
