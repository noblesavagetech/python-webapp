#!/bin/bash

echo "========================================="
echo "  FinHealth Platform - Quick Start"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📦 Installing dependencies (this may take a minute)..."
pip install -r requirements.txt

echo ""
echo "✓ All dependencies installed!"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Creating .env file from template..."
    cp .env.example .env 2>/dev/null || cp .env .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your configuration"
    echo "   At minimum, update SECRET_KEY and JWT_SECRET_KEY"
    echo ""
fi

# Initialize database
echo "🗄️  Initializing database..."
if [ ! -d "migrations" ]; then
    flask db init
    echo "✓ Database migrations initialized"
fi

echo "🗄️  Creating database tables..."
flask db migrate -m "Initial migration" 2>/dev/null || echo "Migration already exists"
flask db upgrade

echo "✓ Database setup complete!"
echo ""

# Create sample questionnaire
echo "📋 Creating sample questionnaire..."
chmod +x scripts/init_questionnaire.sh
./scripts/init_questionnaire.sh

echo ""
echo "========================================="
echo "  🎉 Setup Complete!"
echo "========================================="
echo ""
echo "To start the application:"
echo "  python app.py"
echo ""
echo "Then visit: http://localhost:5000"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Wave Apps credentials"
echo "  2. Start the application: python app.py"
echo "  3. Navigate to http://localhost:5000"
echo "  4. Sign up and complete the questionnaire"
echo ""
echo "For more information, see:"
echo "  - QUICKSTART.md for detailed setup"
echo "  - IMPLEMENTATION.md for technical details"
echo "  - DOCKER.md for Docker deployment"
echo ""
