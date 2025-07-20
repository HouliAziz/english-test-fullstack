from .user import db
from datetime import datetime
from sqlalchemy import func

class UserStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Overall statistics
    total_lessons_completed = db.Column(db.Integer, default=0)
    total_quizzes_taken = db.Column(db.Integer, default=0)
    total_quizzes_passed = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    total_study_time_minutes = db.Column(db.Integer, default=0)
    
    # Level progression
    current_level = db.Column(db.String(20), default='beginner')
    experience_points = db.Column(db.Integer, default=0)
    
    # Streak tracking
    current_streak_days = db.Column(db.Integer, default=0)
    longest_streak_days = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    # Topic-specific performance
    grammar_score = db.Column(db.Float, default=0.0)
    vocabulary_score = db.Column(db.Float, default=0.0)
    reading_score = db.Column(db.Float, default=0.0)
    listening_score = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserStatistics {self.user_id}>'

    def update_quiz_stats(self, quiz_attempt):
        """Update statistics after a quiz attempt"""
        self.total_quizzes_taken += 1
        if quiz_attempt.is_passed:
            self.total_quizzes_passed += 1
        
        # Update average score
        if self.total_quizzes_taken == 1:
            self.average_score = quiz_attempt.score
        else:
            self.average_score = ((self.average_score * (self.total_quizzes_taken - 1)) + quiz_attempt.score) / self.total_quizzes_taken
        
        # Add experience points (raw score, not percentage)
        self.experience_points += int(quiz_attempt.score)
        
        # Update study time
        if quiz_attempt.time_taken_minutes:
            self.total_study_time_minutes += int(quiz_attempt.time_taken_minutes)
        
        self.updated_at = datetime.utcnow()

    def update_lesson_stats(self, lesson):
        """Update statistics after completing a lesson"""
        self.total_lessons_completed += 1
        self.experience_points += 5  # 5 points for completing a lesson
        self.total_study_time_minutes += lesson.duration_minutes
        self.updated_at = datetime.utcnow()

    def update_topic_score(self, topic, score):
        """Update topic-specific scores"""
        topic_mapping = {
            'grammar': 'grammar_score',
            'vocabulary': 'vocabulary_score',
            'reading': 'reading_score',
            'listening': 'listening_score'
        }
        
        if topic in topic_mapping:
            current_score = getattr(self, topic_mapping[topic])
            # Simple moving average (could be improved with more sophisticated algorithm)
            new_score = (current_score + score) / 2 if current_score > 0 else score
            setattr(self, topic_mapping[topic], new_score)

    def update_streak(self):
        """Update daily streak"""
        today = datetime.utcnow().date()
        
        if self.last_activity_date is None:
            self.current_streak_days = 1
            self.last_activity_date = today
        elif self.last_activity_date == today:
            # Already counted today
            return
        elif (today - self.last_activity_date).days == 1:
            # Consecutive day
            self.current_streak_days += 1
            self.last_activity_date = today
        else:
            # Streak broken
            self.current_streak_days = 1
            self.last_activity_date = today
        
        # Update longest streak
        if self.current_streak_days > self.longest_streak_days:
            self.longest_streak_days = self.current_streak_days

    def get_level_progress(self):
        """Calculate level progression based on experience points"""
        levels = {
            'beginner': (0, 100),
            'intermediate': (100, 500),
            'advanced': (500, float('inf'))
        }
        
        for level, (min_xp, max_xp) in levels.items():
            if min_xp <= self.experience_points < max_xp:
                if level != self.current_level:
                    self.current_level = level
                
                progress = min(100, ((self.experience_points - min_xp) / (max_xp - min_xp)) * 100) if max_xp != float('inf') else 100
                return {
                    'current_level': level,
                    'progress_percentage': progress,
                    'xp_current': self.experience_points,
                    'xp_needed': max_xp if max_xp != float('inf') else None
                }
        
        return {
            'current_level': 'advanced',
            'progress_percentage': 100,
            'xp_current': self.experience_points,
            'xp_needed': None
        }

    def get_topic_performance(self):
        from src.models.quiz import QuizAttempt
        attempts = QuizAttempt.query.filter_by(user_id=self.user_id).all()
        topic_scores = {}
        for attempt in attempts:
            topic = None
            if attempt.quiz and attempt.quiz.lesson and hasattr(attempt.quiz.lesson, 'topic'):
                topic = attempt.quiz.lesson.topic.lower()
            if not topic:
                continue
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(attempt.score)
        performance = []
        for topic, scores in topic_scores.items():
            performance.append({
                'topic': topic,
                'average_score': round(sum(scores) / len(scores), 2),
                'attempts': len(scores),
                'best_score': max(scores)
            })
        return performance

    def to_dict(self):
        level_progress = self.get_level_progress()
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_lessons_completed': self.total_lessons_completed,
            'total_quizzes_taken': self.total_quizzes_taken,
            'total_quizzes_passed': self.total_quizzes_passed,
            'pass_rate': round((self.total_quizzes_passed / self.total_quizzes_taken) * 100, 2) if self.total_quizzes_taken > 0 else 0,
            'average_score': round(self.average_score, 2),
            'total_study_time_minutes': self.total_study_time_minutes,
            'total_study_time_hours': round(self.total_study_time_minutes / 60, 2),
            'current_level': self.current_level,
            'experience_points': self.experience_points,
            'level_progress': level_progress,
            'current_streak_days': self.current_streak_days,
            'longest_streak_days': self.longest_streak_days,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'topic_scores': {
                'grammar': round(self.grammar_score, 2),
                'vocabulary': round(self.vocabulary_score, 2),
                'reading': round(self.reading_score, 2),
                'listening': round(self.listening_score, 2)
            },
            'topic_performance': self.get_topic_performance(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

