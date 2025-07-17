from flask import Blueprint, jsonify, request, current_app
from src.models.user import User, db
from src.models.lesson import Lesson
from src.routes.user import token_required
from openai import OpenAI
import json
import os

lesson_bp = Blueprint('lesson', __name__)

def get_openai_client():
    """Get OpenAI client instance"""
    return OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_API_BASE')
    )

def generate_lesson_content(topic, level, duration_minutes=15):
    """Generate lesson content using OpenAI"""
    try:
        client = get_openai_client()
        
        prompt = f"""
        Create an English lesson for {level} level students on the topic of "{topic}".
        The lesson should be approximately {duration_minutes} minutes long.
        
        Please provide the content in the following JSON format:
        {{
            "introduction": "Brief introduction to the topic",
            "objectives": ["Learning objective 1", "Learning objective 2", "Learning objective 3"],
            "content": {{
                "theory": "Main theoretical content explaining the topic",
                "examples": ["Example 1", "Example 2", "Example 3"],
                "practice_exercises": [
                    {{
                        "instruction": "Exercise instruction",
                        "example": "Example of what to do"
                    }}
                ]
            }},
            "vocabulary": [
                {{
                    "word": "vocabulary word",
                    "definition": "definition of the word",
                    "example": "example sentence using the word"
                }}
            ],
            "summary": "Brief summary of what was learned",
            "next_steps": "Suggestions for further learning"
        }}
        
        Make sure the content is appropriate for {level} level and engaging for English learners.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert English teacher creating educational content. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON, if it fails, create a basic structure
        try:
            lesson_data = json.loads(content)
        except json.JSONDecodeError:
            lesson_data = {
                "introduction": f"Welcome to this {level} level lesson on {topic}.",
                "objectives": [f"Understand {topic}", f"Practice {topic}", f"Apply {topic} in context"],
                "content": {
                    "theory": content,
                    "examples": [],
                    "practice_exercises": []
                },
                "vocabulary": [],
                "summary": f"In this lesson, we covered {topic}.",
                "next_steps": "Continue practicing and review the vocabulary."
            }
        
        return lesson_data
        
    except Exception as e:
        # Fallback content if AI generation fails
        return {
            "introduction": f"Welcome to this {level} level lesson on {topic}.",
            "objectives": [
                f"Understand the basics of {topic}",
                f"Learn key vocabulary related to {topic}",
                f"Practice using {topic} in context"
            ],
            "content": {
                "theory": f"This lesson covers the fundamentals of {topic} for {level} level students.",
                "examples": [f"Example 1 for {topic}", f"Example 2 for {topic}"],
                "practice_exercises": [
                    {
                        "instruction": f"Practice exercise for {topic}",
                        "example": f"Example of how to practice {topic}"
                    }
                ]
            },
            "vocabulary": [
                {
                    "word": "example",
                    "definition": "a thing characteristic of its kind or illustrating a general rule",
                    "example": "This is an example sentence."
                }
            ],
            "summary": f"In this lesson, we learned about {topic}.",
            "next_steps": "Continue practicing and review the material."
        }

@lesson_bp.route('/lessons', methods=['GET'])
@token_required
def get_lessons(current_user):
    """Get all lessons"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        level = request.args.get('level')
        topic = request.args.get('topic')
        
        query = Lesson.query.filter_by(is_active=True)
        
        if level:
            query = query.filter_by(level=level)
        if topic:
            query = query.filter(Lesson.topic.ilike(f'%{topic}%'))
        
        lessons = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'lessons': [lesson.to_dict() for lesson in lessons.items],
            'total': lessons.total,
            'pages': lessons.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch lessons'}), 500

@lesson_bp.route('/lessons/<int:lesson_id>', methods=['GET'])
@token_required
def get_lesson(current_user, lesson_id):
    """Get specific lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        return jsonify(lesson.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch lesson'}), 500

@lesson_bp.route('/lessons/generate', methods=['POST'])
@token_required
def generate_lesson(current_user):
    """Generate a new lesson using AI"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['topic', 'level']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        topic = data['topic'].strip()
        level = data['level'].strip().lower()
        duration_minutes = data.get('duration_minutes', 15)
        
        # Validate level
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Level must be beginner, intermediate, or advanced'}), 400
        
        # Generate lesson content using AI
        lesson_content = generate_lesson_content(topic, level, duration_minutes)
        
        # Create lesson title
        title = data.get('title', f"{topic.title()} - {level.title()} Level")
        description = data.get('description', f"Learn about {topic} at {level} level")
        
        # Create new lesson
        lesson = Lesson(
            title=title,
            description=description,
            level=level,
            topic=topic,
            duration_minutes=duration_minutes,
            generated_by_ai=True,
            ai_prompt=f"Topic: {topic}, Level: {level}, Duration: {duration_minutes} minutes"
        )
        lesson.set_content(lesson_content)
        
        db.session.add(lesson)
        db.session.commit()
        
        return jsonify({
            'message': 'Lesson generated successfully',
            'lesson': lesson.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to generate lesson', 'details': str(e)}), 500

@lesson_bp.route('/lessons/<int:lesson_id>', methods=['PUT'])
@token_required
def update_lesson(current_user, lesson_id):
    """Update lesson"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            lesson.title = data['title'].strip()
        if 'description' in data:
            lesson.description = data['description'].strip()
        if 'level' in data and data['level'] in ['beginner', 'intermediate', 'advanced']:
            lesson.level = data['level']
        if 'topic' in data:
            lesson.topic = data['topic'].strip()
        if 'duration_minutes' in data:
            lesson.duration_minutes = data['duration_minutes']
        if 'content' in data:
            lesson.set_content(data['content'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lesson updated successfully',
            'lesson': lesson.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update lesson'}), 500

@lesson_bp.route('/lessons/<int:lesson_id>', methods=['DELETE'])
@token_required
def delete_lesson(current_user, lesson_id):
    """Delete lesson (soft delete)"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        lesson.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Lesson deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete lesson'}), 500

@lesson_bp.route('/lessons/topics', methods=['GET'])
@token_required
def get_topics(current_user):
    """Get available lesson topics"""
    try:
        topics = db.session.query(Lesson.topic).filter_by(is_active=True).distinct().all()
        topic_list = [topic[0] for topic in topics]
        
        return jsonify({
            'topics': topic_list,
            'suggested_topics': [
                'Grammar', 'Vocabulary', 'Reading Comprehension', 'Writing Skills',
                'Speaking Practice', 'Listening Skills', 'Pronunciation', 'Business English',
                'Travel English', 'Academic English', 'Conversation Skills', 'Idioms and Phrases'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch topics'}), 500

