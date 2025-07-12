#!/bin/bash

echo "🚀 Devstral Vision Workspace Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Found: $python_version"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check GPU
echo ""
echo "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠️  No NVIDIA GPU detected. This application requires a CUDA-capable GPU."
fi

# Check Node.js
echo ""
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✅ Found Node.js: $node_version"
else
    echo "⚠️  Node.js not found. Install Node.js for dev server functionality."
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create workspace directory
echo ""
echo "Creating workspace directory..."
mkdir -p workspace
echo "✅ Workspace directory ready"

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python devstral_workspace.py"
echo ""
echo "The interface will open at http://localhost:7865"
echo ""