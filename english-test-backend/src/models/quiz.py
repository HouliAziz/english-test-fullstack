from .user import db
from datetime import datetime
import json


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(
        db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # JSON string containing questions
    questions = db.Column(db.Text, nullable=False)
    # beginner, intermediate, advanced
    level = db.Column(db.String(20), nullable=False)
    # multiple_choice, fill_blank, true_false
    quiz_type = db.Column(db.String(50), default='multiple_choice')
    time_limit_minutes = db.Column(db.Integer, default=10)
    passing_score = db.Column(db.Integer, default=70)  # Percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # AI generation metadata
    generated_by_ai = db.Column(db.Boolean, default=True)
    ai_prompt = db.Column(db.Text, nullable=True)

    # Relations
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

    def __repr__(self):
        return f'<Quiz {self.title}>'

    def set_questions(self, questions_list):
        """Set questions as JSON string"""
        self.questions = json.dumps(questions_list)

    def get_questions(self):
        """Get questions as list"""
        try:
            return json.loads(self.questions)
        except json.JSONDecodeError:
            return []

    def get_questions_without_answers(self):
        """Get questions without correct answers for taking quiz"""
        questions = self.get_questions()
        safe_questions = []
        for q in questions:
            safe_q = {
                'id': q.get('id'),
                'question': q.get('question'),
                'options': q.get('options', []),
                'type': q.get('type', 'multiple_choice')
            }
            safe_questions.append(safe_q)
        return safe_questions

    def calculate_score(self, user_answers):
        """Calculate score based on user answers"""
        questions = self.get_questions()
        if not questions or not isinstance(questions, list):
            print("No questions found for quiz or questions are not a list.")
            return 0

        if not isinstance(user_answers, dict):
            print(f"User answers malformed: {user_answers}")
            return 0

        correct_answers = 0
        total_questions = len(questions)
        if total_questions == 0:
            print("No questions to score (total_questions=0).")
            return 0

        print("Scoring quiz. User answers:", user_answers)
        for question in questions:
            question_id = question.get('id')
            correct_answer = question.get('correct_answer')
            user_answer = user_answers.get(str(question_id))
            print(
                f"---\nQuestion object: {question}\nUser answer: {user_answer}\nCorrect answer: {correct_answer}")
            try:
                if user_answer is not None and correct_answer is not None and str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                    print(f"Answer matched for question {question_id}")
                    correct_answers += 1
                else:
                    print(f"Answer did NOT match for question {question_id}")
            except Exception as e:
                print(
                    f"Error comparing answers for question {question_id}: {e}")

        print(f"Total correct: {correct_answers} / {total_questions}")
        try:
            score = round((correct_answers / total_questions) * 100, 2)
        except Exception as e:
            print(f"Error calculating score: {e}")
            score = 0
        return score

    def to_dict(self, include_answers=False):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'questions': self.get_questions() if include_answers else self.get_questions_without_answers(),
            'level': self.level,
            'quiz_type': self.quiz_type,
            'time_limit_minutes': self.time_limit_minutes,
            'passing_score': self.passing_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'generated_by_ai': self.generated_by_ai,
            'attempt_count': len(self.attempts)
        }


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answers = db.Column(db.Text, nullable=False)  # JSON string of user answers
    score = db.Column(db.Float, nullable=False)  # Percentage score
    time_taken_minutes = db.Column(db.Float, nullable=True)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_passed = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<QuizAttempt {self.user_id}-{self.quiz_id}>'

    def set_answers(self, answers_dict):
        """Set answers as JSON string"""
        self.answers = json.dumps(answers_dict)

    def get_answers(self):
        """Get answers as dictionary"""
        try:
            return json.loads(self.answers)
        except json.JSONDecodeError:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'answers': self.get_answers(),
            'score': self.score,
            'time_taken_minutes': self.time_taken_minutes,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_passed': self.is_passed
        }
