#!/bin/bash
# Quick development server startup script

set -e

echo "🚀 Starting Tax Manager development server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup_dev.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Using .env.example as template."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration."
fi

# Check if database is accessible
echo "🔍 Checking database connection..."
python -c "from app.database import engine; engine.connect()" 2>/dev/null || {
    echo "⚠️  Database connection failed. Make sure PostgreSQL is running:"
    echo "   docker-compose up -d"
    exit 1
}

# Run migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Start server
echo "✅ Starting server on http://localhost:8000"
echo "📚 API docs at http://localhost:8000/docs"
echo ""
python -m app.main
