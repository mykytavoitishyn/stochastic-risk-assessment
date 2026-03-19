#!/usr/bin/env bash
# Start the FastAPI backend and React frontend in parallel.
# Run from the project root or the dashboard/ directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting FastAPI backend on :8000..."
cd "$SCRIPT_DIR" && uvicorn server:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting React frontend on :5173..."
cd "$SCRIPT_DIR/frontend" && npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM
wait
