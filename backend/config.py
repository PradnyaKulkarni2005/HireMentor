import json
import os
from typing import List, Dict, Any

class Config:
    def __init__(self):
        self.questions_file = os.path.join(os.path.dirname(__file__), "questions.json")
        self.questions: List[Dict[str, Any]] = []
        self._load_questions()

    def _load_questions(self):
        """Load questions from JSON file at startup."""
        try:
            with open(self.questions_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

                if isinstance(data, dict):
                    if "questions" in data and isinstance(data["questions"], list):
                        self.questions = data["questions"]
                    else:
                        self.questions = []
                        for category_name, questions in data.items():
                            if isinstance(questions, list):
                                for question in questions:
                                    if isinstance(question, dict):
                                        question_copy = question.copy()
                                        question_copy["category"] = category_name
                                        self.questions.append(question_copy)
                else:
                    self.questions = []
        except FileNotFoundError:
            # Fallback to default questions if file doesn't exist
            self.questions = [
                {
                    "question": "What is OOP?",
                    "keywords": ["class", "object", "inheritance", "polymorphism"],
                    "synonyms": {
                        "class": ["classes"],
                        "object": ["objects", "instance"],
                        "inheritance": ["inherit"],
                        "polymorphism": ["poly", "multiple forms"]
                    }
                },
                {
                    "question": "What is a database?",
                    "keywords": ["data", "storage", "structured"],
                    "synonyms": {
                        "data": ["information", "records"],
                        "storage": ["store", "storing", "persist"],
                        "structured": ["organized", "schema"]
                    }
                }
            ]
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {self.questions_file}")

    def get_categories(self):
        """Return sorted unique categories from loaded questions."""
        categories = {q.get("category", "General") for q in self.questions}
        return sorted(categories)

# Global config instance
config = Config()