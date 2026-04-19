# InterviewIQ

InterviewIQ is a full-stack interview practice app with a React frontend and a FastAPI backend. It lets users choose a category, answer interview questions in a chat-style interface, and receive instant feedback powered by keyword analysis and semantic similarity scoring.

## Project Overview

- Frontend: React + Vite chat experience
- Backend: FastAPI REST API
- Answer evaluation:
  - keyword matching
  - semantic similarity with `sentence-transformers`
- Extras:
  - category-based question flow
  - in-memory user sessions
  - score breakdown and missing-keyword feedback
  - browser voice input support

## Repository Structure

```text
interview-bot/
|-- backend/
|   |-- main.py
|   |-- requirements.txt
|   |-- questions.json
|   |-- routes/
|   |-- services/
|   |-- models/
|   `-- README.md
|-- frontend/
|   |-- package.json
|   |-- src/
|   |-- public/
|   `-- README.md
`-- README.md
```

## How It Works

1. The frontend loads available interview categories from the backend.
2. The user selects a category and receives a question.
3. The user answers by typing or using browser speech recognition.
4. The backend scores the answer using:
   - keyword coverage
   - semantic similarity against an ideal answer
5. The frontend shows feedback, matched keywords, missing concepts, and score details.

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- FastAPI
- Pydantic
- NLTK
- sentence-transformers
- PyTorch
- NumPy

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

## Run The Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('wordnet'); nltk.download('stopwords')"
uvicorn main:app --reload
```

Backend runs at:

- `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

## Run The Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend usually runs at:

- `http://127.0.0.1:5173`

## Frontend To Backend Connection

The frontend uses:

- `VITE_API_URL` if provided
- otherwise `http://127.0.0.1:8000`

Example:

```powershell
$env:VITE_API_URL="http://127.0.0.1:8000"
npm run dev
```

## Main Features

- Category selection before starting the interview
- Chat-style interview flow
- Instant answer feedback
- Matched and missing keyword breakdown
- Combined semantic and keyword scoring
- Session-based question progression
- Voice answer capture in supported browsers

## API Summary

Main backend endpoints:

- `GET /`
- `GET /health`
- `GET /debug`
- `GET /api/v1/categories`
- `GET /api/v1/question`
- `POST /api/v1/answer`
- `GET /api/v1/summary`
- `POST /api/v1/reset`

For backend details, see [backend/README.md](c:\interview-bot\backend\README.md).

## Notes

- Backend sessions are currently stored in memory, so they reset when the server restarts.
- The backend loads the sentence-transformer model on startup and may download it on first run.
- `backend/main.py` currently includes a machine-specific NLTK path: `C:/Users/KULKA/nltk_data`.
- The frontend README is still the default Vite template and may be worth replacing later with project-specific instructions.

## Development Status

The app is functional as a local full-stack project, with room for cleanup and production hardening in areas like:

- persistent session storage
- configurable environment handling
- authentication
- deployment setup
- encoding cleanup in some backend log and message strings
