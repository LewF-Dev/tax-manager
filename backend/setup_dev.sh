#!/bin/bash
# Development setup script

set -e

echo "🚀 Setting up Tax Manager development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration before running the app."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Set up PostgreSQL database"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start dev server: python -m app.main"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
