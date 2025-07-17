#!/usr/bin/env python3
"""
Comprehensive API test script for English Test App Backend
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001/api"

def test_user_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User2"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Registration: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✓ User registered: {result['user']['username']}")
        return result['token']
    else:
        print(f"✗ Registration failed: {response.text}")
        return None

def test_user_login():
    """Test user login"""
    print("\nTesting user login...")
    
    data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Login: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ User logged in: {result['user']['username']}")
        return result['token']
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def test_lesson_generation(token):
    """Test lesson generation"""
    print("\nTesting lesson generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "topic": "Past Tense",
        "level": "intermediate",
        "duration_minutes": 25
    }
    
    response = requests.post(f"{BASE_URL}/lessons/generate", json=data, headers=headers)
    print(f"Lesson generation: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Lesson generated: {result['lesson']['title']}")
        return result['lesson']['id']
    else:
        print(f"✗ Lesson generation failed: {response.text}")
        return None

def test_quiz_generation(token, lesson_id):
    """Test quiz generation"""
    print("\nTesting quiz generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "topic": "Past Tense",
        "level": "intermediate",
        "lesson_id": lesson_id,
        "num_questions": 4
    }
    
    response = requests.post(f"{BASE_URL}/quizzes/generate", json=data, headers=headers)
    print(f"Quiz generation: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Quiz generated: {result['quiz']['title']}")
        return result['quiz']['id']
    else:
        print(f"✗ Quiz generation failed: {response.text}")
        return None

def test_quiz_submission(token, quiz_id):
    """Test quiz submission"""
    print("\nTesting quiz submission...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "answers": {"1": "Correct answer"},
        "time_taken_minutes": 8
    }
    
    response = requests.post(f"{BASE_URL}/quizzes/{quiz_id}/submit", json=data, headers=headers)
    print(f"Quiz submission: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Quiz submitted: Score {result['score']}%")
        return True
    else:
        print(f"✗ Quiz submission failed: {response.text}")
        return False

def test_statistics(token):
    """Test statistics endpoints"""
    print("\nTesting statistics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test dashboard
    response = requests.get(f"{BASE_URL}/statistics/dashboard", headers=headers)
    print(f"Dashboard: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Dashboard loaded: {result['user_statistics']['total_quizzes_taken']} quizzes taken")
    
    # Test achievements
    response = requests.get(f"{BASE_URL}/statistics/achievements", headers=headers)
    print(f"Achievements: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Achievements loaded: {result['total_earned']} earned")
    
    # Test progress
    response = requests.get(f"{BASE_URL}/statistics/progress", headers=headers)
    print(f"Progress: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Progress loaded: {result['overall_stats']['total_attempts']} total attempts")

def test_lessons_list(token):
    """Test lessons listing"""
    print("\nTesting lessons listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/lessons", headers=headers)
    print(f"Lessons list: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Lessons listed: {result['total']} total lessons")

def test_quizzes_list(token):
    """Test quizzes listing"""
    print("\nTesting quizzes listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/quizzes", headers=headers)
    print(f"Quizzes list: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Quizzes listed: {result['total']} total quizzes")

def main():
    """Run all tests"""
    print("=== English Test App Backend API Tests ===\n")
    
    # Test user authentication
    token = test_user_login()
    if not token:
        print("Cannot proceed without authentication token")
        return
    
    # Test lesson generation
    lesson_id = test_lesson_generation(token)
    
    # Test quiz generation
    quiz_id = None
    if lesson_id:
        quiz_id = test_quiz_generation(token, lesson_id)
    
    # Test quiz submission
    if quiz_id:
        test_quiz_submission(token, quiz_id)
    
    # Test statistics
    test_statistics(token)
    
    # Test listing endpoints
    test_lessons_list(token)
    test_quizzes_list(token)
    
    # Test user registration (new user)
    test_user_registration()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()

