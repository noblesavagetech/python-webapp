# Python Flask Web Application

A simple task manager web application built with Flask and SQLite database.

## Features

- ✨ Clean and modern web interface
- 📝 Create, read, update, and delete tasks
- ✅ Mark tasks as complete/incomplete
- 💾 SQLite database backend for data persistence
- 🔌 RESTful API endpoints
- 📱 Responsive design

## Tech Stack

- **Backend**: Python 3.12, Flask 3.0
- **Database**: SQLite with Flask-SQLAlchemy
- **Frontend**: HTML5, CSS3

## Installation

1. Clone the repository:
```bash
git clone https://github.com/noblesavagetech/python-webapp.git
cd python-webapp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

The application will automatically create a SQLite database (`database.db`) on first run.

## API Endpoints

The application provides the following RESTful API endpoints:

### Get all tasks
```
GET /api/tasks
```

### Create a new task
```
POST /api/tasks
Content-Type: application/json

{
  "title": "Task title",
  "description": "Task description (optional)"
}
```

### Get a specific task
```
GET /api/tasks/<task_id>
```

### Update a task
```
PUT /api/tasks/<task_id>
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

### Delete a task
```
DELETE /api/tasks/<task_id>
```

## Web Interface

The web interface provides:
- Form to add new tasks
- List of all tasks with completion status
- Toggle completion status button
- Delete task button
- Statistics showing total, completed, and pending tasks

## Database Schema

### Task Model
- `id`: Integer (Primary Key)
- `title`: String(200) - Task title (required)
- `description`: Text - Task description (optional)
- `completed`: Boolean - Completion status (default: False)
- `created_at`: DateTime - Creation timestamp

## Project Structure

```
python-webapp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface template
├── database.db           # SQLite database (auto-generated)
└── README.md             # This file
```

## License

This project is open source and available for educational purposes.