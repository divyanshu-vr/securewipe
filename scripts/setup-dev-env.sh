#!/bin/bash
# Development environment setup for Linux/Mac

set -e

echo "🔧 Setting up SecureWipe development environment..."

# Check Python version
python3 --version || { echo "❌ Python 3.8+ required"; exit 1; }

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install global development dependencies
echo "📥 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install component dependencies
echo "📥 Installing desktop-app dependencies..."
cd desktop-app && pip install -r requirements.txt && cd ..

echo "📥 Installing bootable-iso dependencies..."
cd bootable-iso && pip install -r requirements.txt && cd ..

echo "📥 Installing shared test dependencies..."
cd shared/tests && pip install -r requirements.txt && cd ../..

# Run initial validation
echo "🧪 Running certificate compatibility tests..."
python scripts/validate-certificates.py

echo "✅ Development environment setup complete!"
echo "💡 Activate with: source venv/bin/activate"