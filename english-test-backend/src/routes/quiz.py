from flask import Blueprint, jsonify, request, current_app
from src.models.user import User, db
from src.models.lesson import Lesson
from src.models.quiz import Quiz, QuizAttempt
from src.models.statistics import UserStatistics
from src.routes.user import token_required
from openai import OpenAI
import json
import os
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)


def get_openai_client():
    """Get OpenAI client instance"""
    return OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_API_BASE')
    )


def generate_quiz_questions(topic, level, num_questions=5, quiz_type='multiple_choice'):
    """Generate quiz questions using OpenAI"""

    try:
        client = get_openai_client()
        prompt = f"""
        Create {num_questions} {quiz_type} questions for {level} level English students on the topic of \"{topic}\".
        Please provide the questions in the following JSON format:
        [
            {{
                "id": 1,
                "question": "Question text here?",
                "type": "{quiz_type}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "Brief explanation of why this is correct"
            }}
        ]
        Guidelines:
        - Make questions appropriate for {level} level
        - Ensure questions test understanding of {topic}
        - Provide clear, unambiguous options
        - Include helpful explanations
        - Questions should be educational and engaging
        """
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert English teacher creating quiz questions. Always respond with valid JSON array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        content = response.choices[0].message.content.strip()
        print("Raw OpenAI response:", content)
        try:
            questions = json.loads(content)
        except Exception as json_err:
            print("JSON decode error:", json_err)
            print("Raw response for debugging:", content)
            raise Exception(
                "OpenAI did not return valid JSON. See logs for details.")
        for i, question in enumerate(questions):
            question['id'] = i + 1
        return questions[:num_questions]
    except Exception as e:
        print(f"AI generation failed: {str(e)}")
        raise Exception(
            "AI quiz generation failed. Please check your OpenAI setup and logs.")


@quiz_bp.route('/quizzes', methods=['GET'])
@token_required
def get_quizzes(current_user):
    """Get all quizzes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        level = request.args.get('level')
        lesson_id = request.args.get('lesson_id', type=int)

        query = Quiz.query.filter_by(is_active=True)

        if level:
            query = query.filter_by(level=level)
        if lesson_id:
            query = query.filter_by(lesson_id=lesson_id)

        quizzes = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'quizzes': [quiz.to_dict() for quiz in quizzes.items],
            'total': quizzes.total,
            'pages': quizzes.pages,
            'current_page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch quizzes'}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@token_required
def get_quiz(current_user, quiz_id):
    """Get specific quiz (without answers for taking quiz)"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        return jsonify(quiz.to_dict(include_answers=False)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch quiz'}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>/answers', methods=['GET'])
@token_required
def get_quiz_with_answers(current_user, quiz_id):
    """Get quiz with answers (for review)"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        return jsonify(quiz.to_dict(include_answers=True)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch quiz'}), 500


@quiz_bp.route('/quizzes/generate', methods=['POST'])
@token_required
def generate_quiz(current_user):
    """Generate a new quiz using AI"""
    try:
        data = request.get_json()
        print(f"Received quiz generation request: {data}")

        # Validate required fields
        required_fields = ['topic', 'level']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400

        topic = data['topic'].strip()
        level = data['level'].strip().lower()
        lesson_id = data.get('lesson_id')
        if not lesson_id:
            return jsonify({'error': 'lesson_id is required'}), 400
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        num_questions = data.get('num_questions', 5)
        quiz_type = data.get('quiz_type', 'multiple_choice')
        time_limit_minutes = data.get('time_limit_minutes', 10)
        passing_score = data.get('passing_score', 70)

        print(
            f"Processing quiz: topic={topic}, level={level}, num_questions={num_questions}")

        # Validate level
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Level must be beginner, intermediate, or advanced'}), 400

        # Generate quiz questions using AI
        print("Generating quiz questions...")
        questions = generate_quiz_questions(
            topic, level, num_questions, quiz_type)
        print(f"Generated {len(questions)} questions")

        # Create quiz title
        title = data.get(
            'title', f"{topic.title()} Quiz - {level.title()} Level")
        description = data.get(
            'description', f"Test your knowledge of {topic} at {level} level")

        # Create new quiz
        print("Creating quiz object...")
        quiz = Quiz(
            lesson_id=lesson_id,
            title=title,
            description=description,
            level=level,
            quiz_type=quiz_type,
            time_limit_minutes=time_limit_minutes,
            passing_score=passing_score,
            generated_by_ai=True,
            ai_prompt=f"Topic: {topic}, Level: {level}, Questions: {num_questions}, Type: {quiz_type}"
        )

        print("Setting questions...")
        quiz.set_questions(questions)

        print("Saving to database...")
        db.session.add(quiz)
        db.session.commit()
        print("Quiz saved successfully")

        return jsonify({
            'message': 'Quiz generated successfully',
            'quiz': quiz.to_dict(include_answers=False)
        }), 201

    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': 'Failed to generate quiz', 'details': str(e)}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@token_required
def submit_quiz(current_user, quiz_id):
    """Submit quiz answers and get score"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()

        if not data.get('answers'):
            return jsonify({'error': 'Answers are required'}), 400

        user_answers = data['answers']
        timings = data.get('timings', {})  # timings is a dict: {question_id: seconds}
        time_taken_minutes = data.get('time_taken_minutes')

        # Calculate score and correct answers
        score, correct_answers = quiz.calculate_score(user_answers, timings)
        total_questions = len(quiz.get_questions())
        accuracy = (correct_answers / total_questions) * 100 if total_questions else 0
        is_passed = score >= quiz.passing_score

        # Create quiz attempt
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score,
            time_taken_minutes=time_taken_minutes,
            is_passed=is_passed
        )
        attempt.set_answers(user_answers)

        db.session.add(attempt)

        # Update user statistics
        stats = UserStatistics.query.filter_by(user_id=current_user.id).first()
        if not stats:
            stats = UserStatistics(user_id=current_user.id)
            db.session.add(stats)

        # Recalculate total points from all attempts
        all_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).all()
        stats.experience_points = sum(int(a.score) for a in all_attempts)
        stats.total_quizzes_taken = len(all_attempts)
        stats.average_score = round(sum(a.score for a in all_attempts) / len(all_attempts), 2) if all_attempts else 0

        # Update topic-specific score if lesson has topic
        if quiz.lesson:
            stats.update_topic_score(quiz.lesson.topic.lower(), score)

        # Update daily streak
        stats.update_streak()

        db.session.commit()

        # Get correct answers for review
        quiz_with_answers = quiz.to_dict(include_answers=True)

        return jsonify({
            'message': 'Quiz submitted successfully',
            'attempt': attempt.to_dict(),
            'score': score,
            'accuracy': accuracy,
            'is_passed': is_passed,
            'quiz_with_answers': quiz_with_answers,
            'statistics': stats.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit quiz', 'details': str(e)}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>/attempts', methods=['GET'])
@token_required
def get_quiz_attempts(current_user, quiz_id):
    """Get user's attempts for a specific quiz"""
    try:
        attempts = QuizAttempt.query.filter_by(
            user_id=current_user.id,
            quiz_id=quiz_id
        ).order_by(QuizAttempt.completed_at.desc()).all()

        return jsonify({
            'attempts': [attempt.to_dict() for attempt in attempts]
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch attempts'}), 500


@quiz_bp.route('/my-attempts', methods=['GET'])
@token_required
def get_my_attempts(current_user):
    """Get all user's quiz attempts"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
            .order_by(QuizAttempt.completed_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        # Include quiz information
        attempts_data = []
        for attempt in attempts.items:
            attempt_dict = attempt.to_dict()
            attempt_dict['quiz'] = attempt.quiz.to_dict(include_answers=False)
            attempts_data.append(attempt_dict)

        return jsonify({
            'attempts': attempts_data,
            'total': attempts.total,
            'pages': attempts.pages,
            'current_page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch attempts'}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@token_required
def update_quiz(current_user, quiz_id):
    """Update quiz"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()

        # Update allowed fields
        if 'title' in data:
            quiz.title = data['title'].strip()
        if 'description' in data:
            quiz.description = data['description'].strip()
        if 'level' in data and data['level'] in ['beginner', 'intermediate', 'advanced']:
            quiz.level = data['level']
        if 'quiz_type' in data:
            quiz.quiz_type = data['quiz_type']
        if 'time_limit_minutes' in data:
            quiz.time_limit_minutes = data['time_limit_minutes']
        if 'passing_score' in data:
            quiz.passing_score = data['passing_score']
        if 'questions' in data:
            quiz.set_questions(data['questions'])

        db.session.commit()

        return jsonify({
            'message': 'Quiz updated successfully',
            'quiz': quiz.to_dict(include_answers=False)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update quiz'}), 500


@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@token_required
def delete_quiz(current_user, quiz_id):
    """Delete quiz (soft delete)"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.is_active = False
        db.session.commit()

        return jsonify({'message': 'Quiz deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete quiz'}), 500
