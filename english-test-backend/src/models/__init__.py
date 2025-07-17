from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .lesson import Lesson
from .quiz import Quiz, QuizAttempt
from .statistics import UserStatistics

