#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID=""

cleanup() {
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo
    echo "Stopping CarbonProof backend..."
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

cd "$PROJECT_DIR"

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm is not installed or is not available on PATH." >&2
  exit 1
fi

if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm_config_cache="${TMPDIR:-/tmp}/carbonproof-npm-cache" npm install
fi

if [[ -n "${DATABASE_URL:-}" ]]; then
  if [[ -x backend/.venv/bin/python ]]; then
    echo "Starting FastAPI backend at http://localhost:8000..."
    backend/.venv/bin/python -m uvicorn api.index:app \
      --app-dir backend \
      --host 127.0.0.1 \
      --port 8000 \
      --reload &
    BACKEND_PID=$!
  else
    echo "DATABASE_URL is set, but backend/.venv is missing."
    echo "Starting the frontend with built-in demo data instead."
  fi
else
  echo "DATABASE_URL is not set; using built-in illustrative demo data."
fi

echo "Starting CarbonProof at http://localhost:3000"
echo "Press Ctrl+C to stop."
echo

WATCHPACK_POLLING="${WATCHPACK_POLLING:-true}" npm run dev
