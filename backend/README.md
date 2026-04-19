# InterviewIQ Backend

FastAPI backend for an interview practice chatbot that scores answers using a mix of keyword matching and semantic similarity.

## What It Does

- Serves interview questions from `questions.json`
- Tracks each user's session in memory
- Evaluates answers with:
  - keyword coverage
  - semantic similarity using `sentence-transformers`
- Returns feedback, scores, and weak-topic summaries

## Tech Stack

- FastAPI
- Pydantic
- NLTK
- sentence-transformers
- PyTorch
- NumPy

## Project Structure

```text
backend/
|-- main.py
|-- config.py
|-- dependencies.py
|-- utils.py
|-- questions.json
|-- requirements.txt
|-- test_api.py
|-- test_import.py
|-- models/
|   `-- schemas.py
|-- routes/
|   `-- interview.py
`-- services/
    |-- analyzer.py
    `-- session.py
```

## Setup

### 1. Create and activate a virtual environment

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install NLTK data

The backend expects `wordnet` and `stopwords`.

```powershell
python -c "import nltk; nltk.download('wordnet'); nltk.download('stopwords')"
```

Note: `main.py` currently appends `C:/Users/KULKA/nltk_data` to the NLTK search path, so if you use a different machine or username, you may want to make that path configurable.

### 4. Start the server

```powershell
uvicorn main:app --reload
```

App URLs:

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## API Endpoints

### `GET /`

Basic status response.

Example response:

```json
{
  "status": "healthy",
  "message": "InterviewIQ API running",
  "docs": "/docs"
}
```

### `GET /health`

Returns service health and version.

### `GET /debug`

Returns registered routes for quick debugging.

### `GET /api/v1/categories`

Returns the available question categories loaded from `questions.json`.

Example response:

```json
{
  "status": "success",
  "data": {
    "categories": ["General", "Python"]
  }
}
```

### `GET /api/v1/question`

Returns a random question and creates or reuses a session.

Query params:

- `category` optional
- `session_id` optional

Example response:

```json
{
  "status": "success",
  "data": {
    "question": "What is OOP?",
    "question_id": "123456789",
    "session_id": "f7c0e1d3-7a6d-4d0f-9dbb-123456789abc",
    "category": "General"
  }
}
```

### `POST /api/v1/answer`

Checks the answer for the current session question.

Request body:

```json
{
  "answer": "OOP uses classes and objects with inheritance and polymorphism.",
  "session_id": "f7c0e1d3-7a6d-4d0f-9dbb-123456789abc"
}
```

Example response:

```json
{
  "status": "success",
  "data": {
    "feedback": "Strong conceptual answer!",
    "matched": ["class", "object", "inheritance"],
    "missing": ["polymorphism"],
    "keyword_score": 0.75,
    "semantic_score": 0.88,
    "final_score": 0.83,
    "score": 0.83
  }
}
```

### `GET /api/v1/summary`

Returns session performance summary.

Query params:

- `session_id` optional

Example response:

```json
{
  "status": "success",
  "data": {
    "average_score": 0.78,
    "weak_topics": ["polymorphism", "abstraction"],
    "questions_answered": 4
  }
}
```

### `POST /api/v1/reset`

Resets session statistics.

Query params:

- `session_id` optional

Example response:

```json
{
  "status": "success",
  "data": {
    "message": "Session reset successfully"
  }
}
```

## Scoring Logic

Answer evaluation combines two signals:

- Keyword score: `40%`
- Semantic score: `60%`

Formula:

```text
final_score = (0.4 * keyword_score) + (0.6 * semantic_score)
```

### Keyword analysis

- lowercases and tokenizes the user answer
- removes stopwords
- lemmatizes words using NLTK
- expands configured synonyms
- uses a lightweight similarity check for near matches

### Semantic analysis

- loads `all-MiniLM-L6-v2` through `SentenceTransformer`
- generates embeddings for the user answer and ideal answer
- computes cosine similarity

If no ideal answer is present, semantic score falls back to `0.0`.

## Question File Format

Questions are loaded from `questions.json`.

Supported shape:

```json
{
  "questions": [
    {
      "question": "What is OOP?",
      "category": "General",
      "keywords": ["class", "object", "inheritance", "polymorphism"],
      "synonyms": {
        "class": ["classes"],
        "object": ["objects", "instance"]
      },
      "ideal_answer": "Object-oriented programming is a programming paradigm based on objects and classes."
    }
  ]
}
```

The loader also supports a category-grouped JSON object and normalizes it internally.

## Session Behavior

- Sessions are stored in memory in `services/session.py`
- A new UUID is created if no valid `session_id` is provided
- Session data is lost when the server restarts

For production, replace in-memory storage with Redis or a database.

## Test Scripts

### Import test

```powershell
python test_import.py
```

Checks whether the backend imports cleanly.

### API smoke test

```powershell
python test_api.py
```

Sends requests to a locally running server at `http://localhost:8000`.

## Known Notes

- The BERT model is loaded on startup and may download on first run.
- NLTK resources must be installed separately.
- CORS is currently open to all origins.
- Logging and some user-facing strings in the codebase still contain encoding artifacts that may be worth cleaning up later.

## Requirements

Current dependencies from `requirements.txt`:

```text
fastapi==0.116.2
uvicorn==0.36.0
pydantic==2.11.9
nltk==3.9.4
sentence-transformers==2.7.0
torch>=2.0.0
numpy>=1.21.0
python-multipart==0.0.20
```
