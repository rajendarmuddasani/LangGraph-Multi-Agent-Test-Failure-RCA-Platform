#!/bin/bash
# Quick start script for Multi-Agent RCA Platform

set -e

echo "🚀 Starting Multi-Agent RCA Platform..."
echo

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update with your API keys before proceeding."
    echo
    read -p "Press Enter after updating .env file, or Ctrl+C to exit..."
fi

# Start Docker services
echo "🐳 Starting Docker services (postgres, redis, qdrant, minio)..."
docker-compose up -d postgres redis qdrant minio

# Wait for services to be ready
echo "⏳ Waiting for services to be ready (15 seconds)..."
sleep 15

# Run database migrations
echo "🗄️  Running Alembic database migrations..."
cd backend
alembic upgrade head

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
if [ ! -f "venv/installed" ]; then
    echo "📦 Installing Python dependencies (this may take a few minutes)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/installed
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed (delete venv/installed to reinstall)"
fi

echo
echo "✅ Backend setup complete!"
echo
echo "To start the backend server:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo
echo "To start the frontend (in another terminal):"
echo "  cd frontend"
echo "  npm install  # first time only"
echo "  npm run dev"
echo
echo "Access points:"
echo "  - Backend API: http://localhost:8000/api/v1/docs"
echo "  - Frontend: http://localhost:3000"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana: http://localhost:3001"
echo
echo "🎉 Ready to analyze test failures!"
