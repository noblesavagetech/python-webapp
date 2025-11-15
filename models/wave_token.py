from extensions import db
from datetime import datetime
import uuid


class WaveToken(db.Model):
    """Stores Wave Apps OAuth tokens per company"""
    __tablename__ = 'wave_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=False, unique=True, index=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    token_type = db.Column(db.String(50), default='Bearer')
    expires_at = db.Column(db.DateTime)
    scope = db.Column(db.String(255))
    wave_business_id = db.Column(db.String(255))  # Wave's business ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<WaveToken {self.company_id}>'
    
    def is_expired(self):
        """Check if token is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'wave_business_id': self.wave_business_id,
            'is_expired': self.is_expired()
        }
