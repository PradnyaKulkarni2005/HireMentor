# Interview Bot Backend

A production-ready FastAPI backend for an AI-powered interview practice chatbot with BERT-based semantic analysis.

## Features

- **Multi-user Session Support**: Session-based conversations with unique IDs
- **Advanced BERT Analysis**: Uses sentence-transformers with all-MiniLM-L6-v2 model for semantic similarity
- **Dual Scoring System**: Combines keyword-based matching (40%) with BERT semantic similarity (60%)
- **Smart Feedback Generation**: Context-aware feedback based on semantic understanding levels
- **Modular Architecture**: Clean separation of concerns with routes, services, models, and utilities
- **Structured API Responses**: Consistent response format with status, data, and messages
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Logging**: Request/response logging for monitoring and debugging
- **Performance Optimization**: Global BERT model loading and efficient embeddings

## API Endpoints

### GET /api/v1/question
Get a random interview question.

**Response:**
```json
{
  "status": "success",
  "data": {
    "question": "What is Object-Oriented Programming (OOP)?",
    "question_id": "123456789",
    "session_id": "session-uuid"
  }
}
```

### POST /api/v1/answer
Submit an answer for evaluation with BERT-based semantic scoring.

**Request:**
```json
{
  "answer": "Object-oriented programming uses classes and objects with inheritance and polymorphism",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "keyword_score": 0.75,
    "semantic_score": 0.82,
    "final_score": 0.79,
    "matched": ["class", "object", "inheritance"],
    "missing": ["polymorphism", "encapsulation"],
    "feedback": "Strong conceptual answer! 🎉 You have excellent understanding of the core concepts."
  }
}
```
    "matched": ["class", "object", "inheritance"],
    "missing": ["polymorphism"],
    "keyword_score": 0.75,
    "semantic_score": 0.886,
    "final_score": 0.818,
    "score": 0.818
  }
}
```

### GET /api/v1/summary
Get session performance summary.

**Response:**
```json
{
  "status": "success",
  "data": {
    "average_score": 0.75,
    "weak_topics": ["inheritance", "polymorphism"],
    "questions_answered": 4
  }
}
```

### POST /api/v1/reset
Reset session data.

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Session reset successfully"
  }
}
```
```json
{
  "status": "success",
  "data": {
    "average_score": 0.75,
    "weak_topics": ["inheritance", "polymorphism"],
    "questions_answered": 4
  }
}
```

### POST /api/reset
Reset session data.

**Response:**
```json
{
  "status": "success",
  "data": {
    "message": "Session reset successfully"
  }
}
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

The BERT model (all-MiniLM-L6-v2) will be downloaded automatically on first startup.

## Configuration

Questions are loaded from `questions.json` at startup. Each question should have:

```json
{
  "question": "What is Object-Oriented Programming (OOP)?",
  "keywords": ["class", "object", "inheritance", "polymorphism", "encapsulation", "abstraction"],
  "synonyms": {
    "class": ["classes"],
    "object": ["objects", "instance"],
    "inheritance": ["inherit", "inherits"]
  },
  "ideal_answer": "Object-oriented programming (OOP) is a programming paradigm based on the concept of objects, which can contain data and code. It uses classes as blueprints for creating objects, and supports four key principles: encapsulation (bundling data and methods), inheritance (classes can inherit properties from parent classes), polymorphism (objects can take many forms), and abstraction (hiding complex implementation details)."
}
```

## Scoring Algorithm

The system combines two analysis methods:

1. **Keyword Analysis** (40% weight): Matches keywords with synonyms and fuzzy matching
2. **Semantic Analysis** (60% weight): Uses BERT embeddings to compare conceptual similarity with ideal answers

**Final Score** = (0.4 × keyword_score) + (0.6 × semantic_score)

## Dependencies

- **sentence-transformers** with `all-MiniLM-L6-v2` model for BERT-based semantic similarity
- **NLTK** for lemmatization and stopwords
- **FastAPI** for the web framework
- **PyTorch** for BERT model inference

## Architecture

```
backend/
├── main.py              # FastAPI app with BERT model loading
├── config.py            # Question loading and configuration
├── dependencies.py      # Dependency injection utilities
├── utils.py             # NLP utilities and helpers
├── models/
│   └── schemas.py       # Pydantic models with semantic fields
├── routes/
│   └── interview.py     # API endpoints with comprehensive analysis
└── services/
    ├── analyzer.py      # Dual keyword + BERT semantic analysis
    └── session.py       # Session management
```

## Development

- Uses FastAPI with automatic OpenAPI documentation at `/docs`
- BERT model loaded once at startup for performance
- Comprehensive logging for debugging semantic analysis
- Modular design for easy testing and extension