from extensions import db
from datetime import datetime
import uuid


class Company(db.Model):
    """Company model - each business that signs up"""
    __tablename__ = 'companies'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))  # small, medium, large
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Questionnaire status
    questionnaire_completed = db.Column(db.Boolean, default=False)
    financial_health_score = db.Column(db.Float)  # Calculated from questionnaire
    
    # Relationships
    users = db.relationship('User', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    questionnaire_responses = db.relationship('QuestionnaireResponse', backref='company', lazy='dynamic', cascade='all, delete-orphan')
    wave_token = db.relationship('WaveToken', backref='company', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'industry': self.industry,
            'size': self.size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'questionnaire_completed': self.questionnaire_completed,
            'financial_health_score': self.financial_health_score,
            'is_active': self.is_active
        }
