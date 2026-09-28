#!/usr/bin/env python3
"""
Quiz engine for the learn system.
Grades quiz answers and provides feedback.
"""

import json
import sys
from typing import Dict, List, Any

def grade_quiz(question: str, correct_answer: str, user_answer: str, options: List[str]) -> Dict[str, Any]:
    """
    Grade a quiz answer.
    
    Args:
        question: The quiz question
        correct_answer: The correct option (must match one in options exactly)
        user_answer: The user's selected option
        options: List of all options
    
    Returns:
        Dict with verdict, explanation, and correctness
    """
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    
    return {
        "correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "feedback": "Correct!" if is_correct else "Not quite. Try again or ask for a hint.",
        "question": question,
        "options": options
    }

def batch_grade(quiz_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Grade multiple quiz questions.
    
    Args:
        quiz_data: List of dicts with 'question', 'correct_answer', 'user_answer', 'options'
    
    Returns:
        Summary with score and detailed results
    """
    results = []
    correct_count = 0
    
    for item in quiz_data:
        result = grade_quiz(
            question=item["question"],
            correct_answer=item["correct_answer"],
            user_answer=item["user_answer"],
            options=item["options"]
        )
        results.append(result)
        if result["correct"]:
            correct_count += 1
    
    return {
        "total": len(results),
        "correct": correct_count,
        "score_percent": round(100 * correct_count / len(results)) if results else 0,
        "results": results
    }

if __name__ == "__main__":
    # Read quiz data from stdin (JSON)
    try:
        quiz_input = json.loads(sys.stdin.read())
        
        if isinstance(quiz_input, list):
            output = batch_grade(quiz_input)
        else:
            output = grade_quiz(
                question=quiz_input["question"],
                correct_answer=quiz_input["correct_answer"],
                user_answer=quiz_input["user_answer"],
                options=quiz_input["options"]
            )
        
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)
