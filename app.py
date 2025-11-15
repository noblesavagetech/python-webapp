import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Render the contact page and handle form submissions"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # In a real application, you would save this to a database or send an email
        return jsonify({
            'success': True,
            'message': f'Thank you {name}! We received your message.'
        })
    return render_template('contact.html')

@app.route('/api/data')
def get_data():
    """API endpoint that returns sample data"""
    sample_data = {
        'items': [
            {'id': 1, 'name': 'Item 1', 'description': 'First sample item'},
            {'id': 2, 'name': 'Item 2', 'description': 'Second sample item'},
            {'id': 3, 'name': 'Item 3', 'description': 'Third sample item'},
        ]
    }
    return jsonify(sample_data)

if __name__ == '__main__':
    # Note: Set FLASK_DEBUG=true environment variable to enable debug mode
    # Debug mode should NEVER be enabled in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
