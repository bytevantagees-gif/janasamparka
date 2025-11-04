#!/bin/bash

# Quick start script for backend
cd "$(dirname "$0")/backend"

echo "🚀 Starting Janasamparka Backend"
echo "================================"

# Activate virtual environment
source .venv/bin/activate

# Run migrations
echo ""
echo "📊 Running database migrations..."
alembic upgrade head

# Load seed data if needed
echo ""
echo "🌱 Checking seed data..."
python seed_data.py 2>&1 | grep -v "already exist" || true

# Start server
echo ""
echo "🚀 Starting FastAPI server..."
echo "   API Docs: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
