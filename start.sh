#!/bin/bash

echo "🚀 Envato Template Finder AI - Startup Script"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if playwright browsers are installed
if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().stop()" 2>/dev/null; then
    echo "🌐 Installing Playwright browsers..."
    playwright install chromium
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Google API key!"
fi

# Start the application
echo ""
echo "✅ Starting server..."
echo "🌐 Open http://localhost:8000 in your browser"
echo ""

python main.py
