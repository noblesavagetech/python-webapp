from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }


# Routes
@app.route('/')
def index():
    """Home page displaying all tasks"""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """API endpoint to get all tasks"""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """API endpoint to create a new task"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', '')
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """API endpoint to get a specific task"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """API endpoint to update a task"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    
    db.session.commit()
    
    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """API endpoint to delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200


@app.route('/task/add', methods=['POST'])
def add_task():
    """Form submission to add a task"""
    title = request.form.get('title')
    description = request.form.get('description', '')
    
    if title:
        task = Task(title=title, description=description)
        db.session.add(task)
        db.session.commit()
    
    return redirect(url_for('index'))


@app.route('/task/toggle/<int:task_id>')
def toggle_task(task_id):
    """Toggle task completion status"""
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    
    return redirect(url_for('index'))


@app.route('/task/delete/<int:task_id>')
def delete_task_web(task_id):
    """Delete a task via web interface"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return redirect(url_for('index'))


# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
