# Python Flask Web Application

A modern, responsive web application built with Python Flask framework, featuring a clean front-end with HTML, CSS, and JavaScript.

## Features

- 🚀 **Flask Backend**: Lightweight and efficient Python web framework
- 🎨 **Responsive Design**: Mobile-friendly interface that works on all devices
- ⚡ **Dynamic Content**: Interactive features with JavaScript and API endpoints
- 📝 **Form Handling**: Contact form with AJAX submission
- 🔄 **RESTful API**: Sample API endpoints for data retrieval
- 🎯 **Clean Code**: Well-structured, maintainable codebase

## Project Structure

```
python-webapp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── about.html        # About page
│   └── contact.html      # Contact page
└── static/               # Static files
    ├── css/
    │   └── style.css     # Main stylesheet
    ├── js/
    │   └── main.js       # JavaScript functionality
    └── images/           # Image assets
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd python-webapp
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask development server:
```bash
python app.py
```

For development with debug mode enabled:
```bash
FLASK_DEBUG=true python app.py
```

**Security Note**: Debug mode should NEVER be enabled in production as it can allow attackers to execute arbitrary code.

2. Open your web browser and navigate to:
```
http://localhost:5000
```

When debug mode is enabled (`FLASK_DEBUG=true`), you get:
- Auto-reload on code changes
- Detailed error messages
- Accessible at `http://0.0.0.0:5000` (visible to other devices on your network)

### Environment Variables

- `FLASK_DEBUG`: Set to `true` to enable debug mode (default: `false`)
- `SECRET_KEY`: Secret key for session management (default: auto-generated)

## Pages

- **Home** (`/`): Landing page with features overview and live API demo
- **About** (`/about`): Information about the project and technologies used
- **Contact** (`/contact`): Contact form with AJAX submission

## API Endpoints

- `GET /api/data`: Returns sample JSON data
  - Example response:
  ```json
  {
    "items": [
      {"id": 1, "name": "Item 1", "description": "First sample item"},
      {"id": 2, "name": "Item 2", "description": "Second sample item"},
      {"id": 3, "name": "Item 3", "description": "Third sample item"}
    ]
  }
  ```

- `POST /contact`: Handles contact form submissions
  - Accepts: name, email, message
  - Returns: JSON success response

## Technologies Used

- **Backend**: Python 3, Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **HTTP Server**: Werkzeug (Flask's development server)

## Development

### Code Style

- Follow PEP 8 guidelines for Python code
- Use semantic HTML5 elements
- Keep CSS organized and well-commented
- Use modern JavaScript (ES6+) features

### Adding New Pages

1. Create a new route in `app.py`:
```python
@app.route('/newpage')
def new_page():
    return render_template('newpage.html')
```

2. Create the template in `templates/newpage.html`:
```html
{% extends "base.html" %}
{% block content %}
<!-- Your content here -->
{% endblock %}
```

### Adding API Endpoints

Add new routes in `app.py`:
```python
@app.route('/api/endpoint')
def api_endpoint():
    return jsonify({'data': 'value'})
```

## Production Deployment

For production deployment, consider:

1. **Ensure debug mode is disabled** (default behavior - do not set `FLASK_DEBUG=true`)
2. Set a strong secret key via environment variable:
   ```bash
   export SECRET_KEY="your-strong-random-secret-key-here"
   ```
3. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 app:app
   ```
4. Set up a reverse proxy (Nginx or Apache)
5. Enable HTTPS/SSL
6. Use a proper database instead of in-memory data
7. Implement proper logging and monitoring

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.