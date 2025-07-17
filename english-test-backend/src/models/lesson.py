from .user import db
from datetime import datetime
import json

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)  # JSON string containing lesson content
    level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    topic = db.Column(db.String(100), nullable=False)  # grammar, vocabulary, reading, etc.
    duration_minutes = db.Column(db.Integer, default=15)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # AI generation metadata
    generated_by_ai = db.Column(db.Boolean, default=True)
    ai_prompt = db.Column(db.Text, nullable=True)  # Store the prompt used for generation
    
    # Relations
    quizzes = db.relationship('Quiz', backref='lesson', lazy=True)

    def __repr__(self):
        return f'<Lesson {self.title}>'

    def set_content(self, content_dict):
        """Set content as JSON string"""
        self.content = json.dumps(content_dict)

    def get_content(self):
        """Get content as dictionary"""
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.get_content(),
            'level': self.level,
            'topic': self.topic,
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'generated_by_ai': self.generated_by_ai,
            'quiz_count': len(self.quizzes)
        }

