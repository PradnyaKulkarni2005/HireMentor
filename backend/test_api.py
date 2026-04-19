#!/usr/bin/env python3
"""
Simple test script to verify the refactored interview bot backend.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_question():
    """Test getting a question."""
    response = requests.get(f"{BASE_URL}/api/v1/question")
    print(f"Get question: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data["data"]["question_id"] if "data" in data else None
    return None

def test_answer(question_id, session_id=None):
    """Test submitting an answer."""
    payload = {
        "answer": "Object-oriented programming uses classes, objects, inheritance, and polymorphism to organize code.",
        "session_id": session_id
    }
    response = requests.post(f"{BASE_URL}/api/v1/answer", json=payload)
    print(f"Submit answer: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data.get("status") == "success"
    return False

def test_summary(session_id=None):
    """Test getting summary."""
    params = {"session_id": session_id} if session_id else {}
    response = requests.get(f"{BASE_URL}/api/v1/summary", params=params)
    print(f"Get summary: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    return response.status_code == 200

def test_reset(session_id=None):
    """Test resetting session."""
    payload = {"session_id": session_id} if session_id else {}
    response = requests.post(f"{BASE_URL}/api/v1/reset", json=payload)
    print(f"Reset session: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing Interview Bot Backend...")
    print("=" * 50)

    # Test health
    if not test_health():
        print("Health check failed!")
        exit(1)

    print("\n" + "=" * 50)

    # Test question
    question_id = test_question()
    if not question_id:
        print("Failed to get question!")
        exit(1)

    print("\n" + "=" * 50)

    # Test answer
    if not test_answer(question_id):
        print("Failed to submit answer!")
        exit(1)

    print("\n" + "=" * 50)

    # Test summary
    if not test_summary():
        print("Failed to get summary!")
        exit(1)

    print("\n" + "=" * 50)

    # Test reset
    if not test_reset():
        print("Failed to reset session!")
        exit(1)

    print("\n" + "=" * 50)
    print("All tests passed! 🎉")