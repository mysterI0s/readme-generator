#!/bin/bash

# README Generator Setup Script
# This script sets up the README Generator project

set -e  # Exit on any error

echo "🚀 Setting up README Generator..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Create project structure
echo "📁 Creating project structure..."

# Create directories
mkdir -p src
mkdir -p tests
mkdir -p examples
mkdir -p docs

# Create __init__.py files
touch src/__init__.py
touch tests/__init__.py

echo "✅ Project structure created"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "✅ Dependencies installed"

# Create example configuration file
if [ ! -f "config.example.json" ]; then
    echo "⚙️ Creating example configuration..."
    cat > config.example.json << EOF
{
  "model_name": "openai/gpt-4o",
  "api_base_url": "https://openrouter.ai/api/v1",
  "max_file_size": 100000,
  "max_files": 50,
  "readme_template": "comprehensive",
  "include_badges": true,
  "include_toc": true,
  "include_installation": true,
  "include_usage": true,
  "include_api_docs": true,
  "include_contributing": true,
  "include_license": true,
  "request_timeout": 30,
  "max_retries": 3,
  "retry_delay": 1.0
}
EOF
    echo "✅ Example configuration created"
fi

# Create .env.example file
if [ ! -f ".env.example" ]; then
    echo "🔑 Creating environment variable example..."
    cat > .env.example << EOF
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Override default model
# MODEL_NAME=openai/gpt-4o

# Optional: Override API base URL
# API_BASE_URL=https://openrouter.ai/api/v1
EOF
    echo "✅ Environment example created"
fi

# Make main script executable
if [ -f "main.py" ]; then
    chmod +x main.py
    echo "✅ Made main.py executable"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Generated files
README_generated.md
*.log

# Test coverage
.coverage
htmlcov/
.pytest_cache/
EOF
    echo "✅ .gitignore created"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your OpenRouter API key:"
echo "   cp .env.example .env"
echo "   # Edit .env and add your API key"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Test the installation:"
echo "   python main.py --help"
echo ""
echo "4. Generate a README for a repository:"
echo "   python main.py https://github.com/user/repo"
echo ""
echo "Happy README generating! 🚀"