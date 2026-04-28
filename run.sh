#!/usr/bin/env bash
# run.sh — Start the Chat with PDF server
# Usage: ./run.sh
# This script activates the virtual environment automatically before starting.

set -e  # Exit on any error

# Project directory (same folder as this script)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# Check venv exists
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "❌ Virtual environment not found at: $VENV_DIR"
  echo "   Run this first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# Activate the venv
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated: $VENV_DIR"

# Check .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo "⚠️  Warning: .env file not found. Copying from .env.example..."
  cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
  echo "   ➡️  Edit .env and add your XAI_API_KEY before chatting!"
fi

# Free port 8000 if already in use
if lsof -ti:8000 >/dev/null 2>&1; then
  echo "⚠️  Port 8000 is in use. Killing existing process..."
  lsof -ti:8000 | xargs kill -9 2>/dev/null || true
  sleep 1
fi

echo ""
echo "🚀 Starting Chat with PDF..."
echo "   Open your browser at: http://localhost:8000"
echo "   Press Ctrl+C to stop."
echo ""

# Start app
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
