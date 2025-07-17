from flask import Blueprint, jsonify, request, current_app
from src.models.user import User, db
from src.models.lesson import Lesson
from src.models.quiz import Quiz, QuizAttempt
from src.models.statistics import UserStatistics
from src.routes.user import token_required
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/statistics/dashboard', methods=['GET'])
@token_required
def get_dashboard(current_user):
    """Get user dashboard statistics"""
    try:
        # Get user statistics
        stats = UserStatistics.query.filter_by(user_id=current_user.id).first()
        if not stats:
            stats = UserStatistics(user_id=current_user.id)
            db.session.add(stats)
            db.session.commit()
        
        # Get recent quiz attempts (last 10)
        recent_attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
            .order_by(desc(QuizAttempt.completed_at))\
            .limit(10).all()
        
        # Get recent attempts with quiz info
        recent_attempts_data = []
        for attempt in recent_attempts:
            attempt_dict = attempt.to_dict()
            attempt_dict['quiz_title'] = attempt.quiz.title
            attempt_dict['quiz_topic'] = attempt.quiz.lesson.topic if attempt.quiz.lesson else 'General'
            recent_attempts_data.append(attempt_dict)
        
        # Calculate weekly progress (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.completed_at >= week_ago
        ).all()
        
        daily_progress = {}
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_progress[date] = {
                'quizzes_taken': 0,
                'average_score': 0,
                'time_spent': 0
            }
        
        for attempt in weekly_attempts:
            date = attempt.completed_at.strftime('%Y-%m-%d')
            if date in daily_progress:
                daily_progress[date]['quizzes_taken'] += 1
                daily_progress[date]['time_spent'] += attempt.time_taken_minutes or 0
        
        # Calculate average scores for each day
        for date in daily_progress:
            day_attempts = [a for a in weekly_attempts if a.completed_at.strftime('%Y-%m-%d') == date]
            if day_attempts:
                daily_progress[date]['average_score'] = sum(a.score for a in day_attempts) / len(day_attempts)
        
        # Get level recommendations
        recommendations = get_level_recommendations(current_user, stats)
        
        return jsonify({
            'user_statistics': stats.to_dict(),
            'recent_attempts': recent_attempts_data,
            'weekly_progress': daily_progress,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch dashboard', 'details': str(e)}), 500

@statistics_bp.route('/statistics/progress', methods=['GET'])
@token_required
def get_progress(current_user):
    """Get detailed progress statistics"""
    try:
        # Get time period from query params
        period = request.args.get('period', 'month')  # week, month, year, all
        
        # Calculate date range
        if period == 'week':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == 'year':
            start_date = datetime.utcnow() - timedelta(days=365)
        else:  # all
            start_date = datetime.min
        
        # Get quiz attempts in period
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.completed_at >= start_date
        ).order_by(QuizAttempt.completed_at).all()
        
        # Group by topic
        topic_stats = {}
        for attempt in attempts:
            topic = 'General'
            if attempt.quiz.lesson:
                topic = attempt.quiz.lesson.topic
            
            if topic not in topic_stats:
                topic_stats[topic] = {
                    'attempts': 0,
                    'total_score': 0,
                    'passed': 0,
                    'time_spent': 0,
                    'scores': []
                }
            
            topic_stats[topic]['attempts'] += 1
            topic_stats[topic]['total_score'] += attempt.score
            topic_stats[topic]['time_spent'] += attempt.time_taken_minutes or 0
            topic_stats[topic]['scores'].append(attempt.score)
            if attempt.is_passed:
                topic_stats[topic]['passed'] += 1
        
        # Calculate averages and trends
        for topic in topic_stats:
            stats = topic_stats[topic]
            stats['average_score'] = stats['total_score'] / stats['attempts'] if stats['attempts'] > 0 else 0
            stats['pass_rate'] = (stats['passed'] / stats['attempts']) * 100 if stats['attempts'] > 0 else 0
            stats['average_time'] = stats['time_spent'] / stats['attempts'] if stats['attempts'] > 0 else 0
            
            # Calculate trend (improvement over time)
            if len(stats['scores']) >= 2:
                first_half = stats['scores'][:len(stats['scores'])//2]
                second_half = stats['scores'][len(stats['scores'])//2:]
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                stats['trend'] = second_avg - first_avg
            else:
                stats['trend'] = 0
            
            # Remove raw scores from response
            del stats['scores']
        
        # Get overall statistics
        overall_stats = {
            'total_attempts': len(attempts),
            'average_score': sum(a.score for a in attempts) / len(attempts) if attempts else 0,
            'total_time_spent': sum(a.time_taken_minutes or 0 for a in attempts),
            'pass_rate': (sum(1 for a in attempts if a.is_passed) / len(attempts)) * 100 if attempts else 0
        }
        
        return jsonify({
            'period': period,
            'overall_stats': overall_stats,
            'topic_stats': topic_stats,
            'total_topics': len(topic_stats)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch progress', 'details': str(e)}), 500

@statistics_bp.route('/statistics/leaderboard', methods=['GET'])
@token_required
def get_leaderboard(current_user):
    """Get leaderboard statistics"""
    try:
        # Get top users by experience points
        top_users = db.session.query(
            User.username,
            User.level,
            UserStatistics.experience_points,
            UserStatistics.total_quizzes_taken,
            UserStatistics.average_score,
            UserStatistics.current_streak_days
        ).join(UserStatistics, User.id == UserStatistics.user_id)\
         .order_by(desc(UserStatistics.experience_points))\
         .limit(10).all()
        
        leaderboard = []
        current_user_rank = None
        
        for i, user_data in enumerate(top_users):
            user_info = {
                'rank': i + 1,
                'username': user_data.username,
                'level': user_data.level,
                'experience_points': user_data.experience_points,
                'total_quizzes': user_data.total_quizzes_taken,
                'average_score': round(user_data.average_score, 1),
                'current_streak': user_data.current_streak_days
            }
            leaderboard.append(user_info)
            
            if user_data.username == current_user.username:
                current_user_rank = i + 1
        
        # If current user is not in top 10, find their rank
        if current_user_rank is None:
            user_rank_query = db.session.query(func.count(UserStatistics.id))\
                .filter(UserStatistics.experience_points > 
                       UserStatistics.query.filter_by(user_id=current_user.id).first().experience_points)\
                .scalar()
            current_user_rank = user_rank_query + 1
        
        return jsonify({
            'leaderboard': leaderboard,
            'current_user_rank': current_user_rank,
            'total_users': User.query.count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch leaderboard', 'details': str(e)}), 500

@statistics_bp.route('/statistics/achievements', methods=['GET'])
@token_required
def get_achievements(current_user):
    """Get user achievements and badges"""
    try:
        stats = UserStatistics.query.filter_by(user_id=current_user.id).first()
        if not stats:
            return jsonify({'achievements': [], 'progress': {}}), 200
        
        achievements = []
        progress = {}
        
        # Define achievement criteria
        achievement_criteria = {
            'first_quiz': {
                'name': 'First Steps',
                'description': 'Complete your first quiz',
                'icon': '🎯',
                'condition': stats.total_quizzes_taken >= 1
            },
            'quiz_master': {
                'name': 'Quiz Master',
                'description': 'Complete 10 quizzes',
                'icon': '🏆',
                'condition': stats.total_quizzes_taken >= 10,
                'progress_current': stats.total_quizzes_taken,
                'progress_target': 10
            },
            'perfect_score': {
                'name': 'Perfect Score',
                'description': 'Get 100% on a quiz',
                'icon': '⭐',
                'condition': QuizAttempt.query.filter_by(user_id=current_user.id, score=100.0).first() is not None
            },
            'streak_week': {
                'name': 'Week Warrior',
                'description': 'Maintain a 7-day streak',
                'icon': '🔥',
                'condition': stats.current_streak_days >= 7,
                'progress_current': stats.current_streak_days,
                'progress_target': 7
            },
            'high_achiever': {
                'name': 'High Achiever',
                'description': 'Maintain 90% average score',
                'icon': '🌟',
                'condition': stats.average_score >= 90,
                'progress_current': round(stats.average_score, 1),
                'progress_target': 90
            },
            'level_up': {
                'name': 'Level Up',
                'description': 'Reach intermediate level',
                'icon': '📈',
                'condition': stats.current_level in ['intermediate', 'advanced']
            },
            'advanced_learner': {
                'name': 'Advanced Learner',
                'description': 'Reach advanced level',
                'icon': '🎓',
                'condition': stats.current_level == 'advanced'
            }
        }
        
        # Check achievements
        for key, criteria in achievement_criteria.items():
            if criteria['condition']:
                achievements.append({
                    'id': key,
                    'name': criteria['name'],
                    'description': criteria['description'],
                    'icon': criteria['icon'],
                    'earned': True,
                    'earned_date': stats.updated_at.isoformat()
                })
            else:
                # Track progress for unearned achievements
                if 'progress_current' in criteria:
                    progress[key] = {
                        'name': criteria['name'],
                        'description': criteria['description'],
                        'icon': criteria['icon'],
                        'current': criteria['progress_current'],
                        'target': criteria['progress_target'],
                        'percentage': min(100, (criteria['progress_current'] / criteria['progress_target']) * 100)
                    }
        
        return jsonify({
            'achievements': achievements,
            'progress': progress,
            'total_earned': len(achievements)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch achievements', 'details': str(e)}), 500

@statistics_bp.route('/statistics/export', methods=['GET'])
@token_required
def export_statistics(current_user):
    """Export user statistics as JSON"""
    try:
        # Get all user data
        stats = UserStatistics.query.filter_by(user_id=current_user.id).first()
        attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
            .order_by(QuizAttempt.completed_at).all()
        
        # Prepare export data
        export_data = {
            'user': current_user.to_dict(),
            'statistics': stats.to_dict() if stats else None,
            'quiz_attempts': [attempt.to_dict() for attempt in attempts],
            'export_date': datetime.utcnow().isoformat(),
            'total_attempts': len(attempts)
        }
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to export statistics', 'details': str(e)}), 500

def get_level_recommendations(user, stats):
    """Get personalized learning recommendations"""
    recommendations = []
    
    # Based on performance
    if stats.average_score < 70:
        recommendations.append({
            'type': 'improvement',
            'title': 'Focus on Fundamentals',
            'description': 'Your average score is below 70%. Consider reviewing basic concepts.',
            'action': 'Take beginner level quizzes'
        })
    elif stats.average_score > 85 and user.level == 'beginner':
        recommendations.append({
            'type': 'advancement',
            'title': 'Ready for Next Level',
            'description': 'Your performance suggests you\'re ready for intermediate level.',
            'action': 'Try intermediate quizzes'
        })
    
    # Based on activity
    if stats.current_streak_days == 0:
        recommendations.append({
            'type': 'motivation',
            'title': 'Get Back on Track',
            'description': 'Start a new learning streak today!',
            'action': 'Take a quick quiz'
        })
    elif stats.current_streak_days >= 7:
        recommendations.append({
            'type': 'congratulations',
            'title': 'Great Streak!',
            'description': f'You\'ve maintained a {stats.current_streak_days}-day streak. Keep it up!',
            'action': 'Continue your momentum'
        })
    
    # Based on topic performance
    weak_topics = []
    if stats.grammar_score > 0 and stats.grammar_score < 70:
        weak_topics.append('grammar')
    if stats.vocabulary_score > 0 and stats.vocabulary_score < 70:
        weak_topics.append('vocabulary')
    if stats.reading_score > 0 and stats.reading_score < 70:
        weak_topics.append('reading')
    
    if weak_topics:
        recommendations.append({
            'type': 'focus',
            'title': 'Strengthen Weak Areas',
            'description': f'Consider focusing on: {", ".join(weak_topics)}',
            'action': f'Practice {weak_topics[0]} exercises'
        })
    
    return recommendations

