#!/bin/bash
# Railway production startup script

echo "Starting Railway deployment..."

# Set Flask environment
export FLASK_APP=app.py
export FLASK_ENV=production

# Wait for database to be ready (Railway handles this, but add a small delay)
sleep 5

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Initialize questionnaire data
echo "Initializing questionnaire data..."
python scripts/init_questionnaire.py

# Start the application
echo "Starting Flask application..."
python app.py