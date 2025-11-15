from extensions import db
from datetime import datetime
import uuid
import json


class Questionnaire(db.Model):
    """Questionnaire template - defines questions for financial health assessment"""
    __tablename__ = 'questionnaires'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    questions = db.Column(db.JSON, nullable=False)  # Array of question objects
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Questionnaire {self.title} v{self.version}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'questions': self.questions,
            'version': self.version,
            'is_active': self.is_active
        }


class QuestionnaireResponse(db.Model):
    """Stores company responses to questionnaire"""
    __tablename__ = 'questionnaire_responses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=False, index=True)
    questionnaire_id = db.Column(db.String(36), db.ForeignKey('questionnaires.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)  # Dictionary of question_id: answer
    score = db.Column(db.Float)  # Calculated financial health score
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    questionnaire = db.relationship('Questionnaire', backref='responses')
    
    def __repr__(self):
        return f'<QuestionnaireResponse {self.company_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'questionnaire_id': self.questionnaire_id,
            'answers': self.answers,
            'score': self.score,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
