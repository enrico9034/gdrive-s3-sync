#!/bin/bash

# Script di setup per l'ambiente di sviluppo

echo "🚀 Setup S3 to Google Drive Sync"
echo "=================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "  ✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "  ✓ Virtual environment activated"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  ✓ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p credentials
mkdir -p logs
echo "  ✓ Directories created"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "  ✓ .env file created from template"
    echo "  ⚠️  PLEASE EDIT .env WITH YOUR CREDENTIALS!"
else
    echo "✓ .env file already exists"
fi
echo ""

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your AWS and Google Drive credentials"
echo "2. Download credentials.json from Google Cloud Console"
echo "3. Place credentials.json in the credentials/ folder"
echo "4. Run: source venv/bin/activate"
echo "5. Run: python main.py"
echo ""
echo "Or use Docker:"
echo "1. Complete steps 1-3 above"
echo "2. Run: docker-compose up -d"
echo ""
