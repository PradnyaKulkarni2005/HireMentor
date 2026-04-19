from typing import Optional
from fastapi import Depends, HTTPException
from services.session import get_or_create_session

def get_session_id(session_id: Optional[str] = None) -> str:
    """Dependency to get or create session ID."""
    return get_or_create_session(session_id)