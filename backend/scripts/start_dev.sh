#!/bin/bash
# Quick development server starter

echo "🛡️  Starting Vulnerability Scanner Development Environment"

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

# Check environment
echo "🔍 Checking environment..."
python run.py --check-only

if [ $? -eq 0 ]; then
    echo "✅ Environment OK"
else
    echo "⚠️  Environment issues detected, but continuing..."
fi

# Start server
echo "🚀 Starting development server..."
python run.py --debug --host 0.0.0.0 --port 5000