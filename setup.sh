#!/bin/bash

echo "Setting up Financial Health Tracking Platform..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "✓ .env file created - please update with your credentials"
else
    echo "✓ .env file already exists"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! Next steps:"
echo ""
echo "1. Update .env file with your configuration:"
echo "   - Database connection string"
echo "   - Wave Apps credentials"
echo "   - Secret keys"
echo ""
echo "2. Initialize the database:"
echo "   flask db init"
echo "   flask db migrate -m 'Initial migration'"
echo "   flask db upgrade"
echo ""
echo "3. Create sample questionnaire:"
echo "   chmod +x scripts/init_questionnaire.sh"
echo "   ./scripts/init_questionnaire.sh"
echo ""
echo "4. Run the application:"
echo "   python app.py"
echo ""
