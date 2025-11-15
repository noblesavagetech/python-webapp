from flask import render_template, send_from_directory
from app import create_app
import os

app = create_app()

# Route handlers for HTML pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
