from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

class AnswerRequest(BaseModel):
    answer: str
    session_id: Optional[str] = None

class QuestionResponse(BaseModel):
    question: str
    question_id: str
    session_id: str
    category: Optional[str] = None

class AnswerResponse(BaseModel):
    feedback: str
    matched: List[str]
    missing: List[str]
    keyword_score: float
    semantic_score: float
    final_score: float
    # Keep score for backward compatibility (same as final_score)
    score: float

class SummaryResponse(BaseModel):
    average_score: float
    weak_topics: List[str]
    questions_answered: int

class ResetResponse(BaseModel):
    message: str

class APIResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: Optional[str] = None

class SessionData(BaseModel):
    score: float
    questions_answered: int
    weak_topics: Dict[str, int]
    current_question: Optional[Dict[str, Any]] = None