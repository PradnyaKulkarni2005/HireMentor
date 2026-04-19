import logging
import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from models.schemas import (
    AnswerRequest, QuestionResponse, AnswerResponse,
    SummaryResponse, ResetResponse, APIResponse
)
from services.analyzer import analyze_answer_comprehensive, generate_enhanced_feedback
from services.session import (
    get_session_summary, reset_session as reset_session_service,
    set_current_question, get_current_question, get_session
)
from config import config
from dependencies import get_session_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/question", response_model=APIResponse)
def get_question(
    category: Optional[str] = None,
    session_id: str = Depends(get_session_id)
):
    """Get a random question for the session, optionally filtered by category."""
    try:
        if not config.questions:
            raise HTTPException(status_code=500, detail="No questions available")

        questions = config.questions
        if category:
            questions = [
                q for q in config.questions
                if q.get("category", "General").lower() == category.lower()
            ]
            if not questions:
                raise HTTPException(status_code=404, detail="No questions available for selected category")

        question_data = random.choice(questions)
        question_id = str(hash((question_data.get("question"), question_data.get("category"))))

        # Set current question for session
        set_current_question(session_id, {**question_data, "id": question_id})

        response_data = QuestionResponse(
            question=question_data["question"],
            question_id=question_id,
            session_id=session_id,
            category=question_data.get("category", "General")
        )

        logger.info(f"Session {session_id}: Question served - {question_data['question'][:50]}...")

        return APIResponse(
            status="success",
            data=response_data.dict()
        )
    except Exception as e:
        logger.error(f"Error getting question for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get question")

@router.get("/categories", response_model=APIResponse)
def get_categories():
    """Return available question categories."""
    try:
        logger.info("📋 Categories endpoint called")
        
        if not config.questions:
            logger.error("No questions loaded")
            raise HTTPException(status_code=500, detail="No questions available")

        categories = config.get_categories()
        logger.info(f"✅ Returning {len(categories)} categories: {categories}")
        
        return APIResponse(
            status="success",
            data={"categories": categories}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting categories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get categories")

@router.post("/answer", response_model=APIResponse)
def check_answer(
    request: AnswerRequest,
    session_id: str = Depends(get_session_id)
):
    """Check user's answer and provide feedback."""
    try:
        # Get current question
        current_question = get_current_question(session_id)
        if not current_question:
            return APIResponse(
                status="error",
                data={},
                message="No question asked yet. Please get a question first."
            )

        # Analyze answer with comprehensive scoring
        analysis_result = analyze_answer_comprehensive(
            request.answer,
            current_question["keywords"],
            current_question.get("ideal_answer"),
            current_question.get("synonyms", {})
        )

        # Generate enhanced feedback
        feedback = generate_enhanced_feedback(
            analysis_result["keyword_score"],
            analysis_result["semantic_score"],
            analysis_result["final_score"],
            analysis_result["matched"],
            analysis_result["missing"]
        )

        # Update session with final score
        from services.session import update_session
        update_session(session_id, analysis_result["final_score"], analysis_result["missing"])

        response_data = AnswerResponse(
            feedback=feedback,
            matched=analysis_result["matched"],
            missing=analysis_result["missing"],
            keyword_score=analysis_result["keyword_score"],
            semantic_score=analysis_result["semantic_score"],
            final_score=analysis_result["final_score"],
            score=analysis_result["final_score"]  # Backward compatibility
        )

        logger.info(f"Session {session_id}: Answer processed - Keyword: {analysis_result['keyword_score']:.2f}, Semantic: {analysis_result['semantic_score']:.2f}, Final: {analysis_result['final_score']:.2f}")

        return APIResponse(
            status="success",
            data=response_data.dict()
        )

    except Exception as e:
        logger.error(f"Error processing answer for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process answer")

@router.get("/summary", response_model=APIResponse)
def get_summary(session_id: str = Depends(get_session_id)):
    """Get session summary statistics."""
    try:
        summary = get_session_summary(session_id)
        if not summary:
            return APIResponse(
                status="success",
                data={"message": "No data yet"},
                message="Session has no completed questions yet"
            )

        response_data = SummaryResponse(**summary)

        return APIResponse(
            status="success",
            data=response_data.dict()
        )

    except Exception as e:
        logger.error(f"Error getting summary for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get summary")

@router.post("/reset", response_model=APIResponse)
def reset_session(session_id: str = Depends(get_session_id)):
    """Reset session data."""
    try:
        success = reset_session_service(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        response_data = ResetResponse(message="Session reset successfully")

        logger.info(f"Session {session_id}: Session reset")

        return APIResponse(
            status="success",
            data=response_data.dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset session")