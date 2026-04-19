import uuid
from typing import Dict, List, Optional, Any
from models.schemas import SessionData

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, SessionData] = {}

def get_or_create_session(session_id: Optional[str] = None) -> str:
    """Get existing session or create new one."""
    if session_id and session_id in sessions:
        return session_id

    # Create new session
    new_session_id = session_id or str(uuid.uuid4())
    sessions[new_session_id] = SessionData(
        score=0.0,
        questions_answered=0,
        weak_topics={},
        current_question=None
    )
    return new_session_id

def get_session(session_id: str) -> Optional[SessionData]:
    """Get session data by ID."""
    return sessions.get(session_id)

def update_session(session_id: str, score: float, missing: List[str], current_question: Optional[Dict[str, Any]] = None):
    """Update session with answer results."""
    session = get_session(session_id)
    if not session:
        return

    session.questions_answered += 1
    session.score += score
    session.current_question = current_question

    for topic in missing:
        session.weak_topics[topic] = session.weak_topics.get(topic, 0) + 1

def get_session_summary(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session summary statistics."""
    session = get_session(session_id)
    if not session or session.questions_answered == 0:
        return None

    avg_score = session.score / session.questions_answered

    weak_topics = sorted(
        session.weak_topics.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "average_score": round(avg_score, 2),
        "weak_topics": [topic for topic, _ in weak_topics[:3]],
        "questions_answered": session.questions_answered
    }

def reset_session(session_id: str) -> bool:
    """Reset session data."""
    if session_id in sessions:
        sessions[session_id] = SessionData(
            score=0.0,
            questions_answered=0,
            weak_topics={},
            current_question=None
        )
        return True
    return False

def set_current_question(session_id: str, question: Dict[str, Any]):
    """Set current question for session."""
    session = get_session(session_id)
    if session:
        session.current_question = question

def get_current_question(session_id: str) -> Optional[Dict[str, Any]]:
    """Get current question for session."""
    session = get_session(session_id)
    return session.current_question if session else None

def cleanup_old_sessions():
    """Clean up old sessions (implement TTL logic if needed)."""
    # For now, keep all sessions. In production, implement cleanup based on last activity
    pass