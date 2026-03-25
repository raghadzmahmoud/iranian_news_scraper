#!/bin/bash

# Setup and Run X Scraper Locally
# تجهيز وتشغيل السحب من X محليًا

set -e

echo "=================================================="
echo "🔧 X Scraper Local Setup & Run"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "📥 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python -m playwright install chromium

# Run the scraper
echo ""
echo "=================================================="
echo "🚀 Starting X Scraper..."
echo "=================================================="
echo ""

python run_x_scraper_local.py

echo ""
echo "=================================================="
echo "✅ Done!"
echo "=================================================="
