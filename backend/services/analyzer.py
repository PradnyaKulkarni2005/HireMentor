from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Any, Optional
from utils import preprocess_text, calculate_similarity, expand_keywords_with_synonyms

# Global BERT model - loaded once at startup
bert_model = None

def load_bert_model():
    """
    Load BERT model globally. Call this once at startup.
    Uses 'all-MiniLM-L6-v2' for efficient sentence embeddings.
    """
    global bert_model
    if bert_model is None:
        try:
            bert_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ BERT model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load BERT model: {e}")
            bert_model = None

def get_bert_model():
    """Get the loaded BERT model."""
    return bert_model

def semantic_score(user_answer: str, ideal_answer: str) -> float:
    """
    Calculate semantic similarity between user answer and ideal answer using BERT embeddings.

    Args:
        user_answer: The user's response
        ideal_answer: The ideal/reference answer

    Returns:
        Similarity score between 0.0 and 1.0 using cosine similarity of embeddings
    """
    global bert_model
    if not bert_model:
        print("DEBUG: BERT model not loaded, loading now...")
        load_bert_model()

    if not bert_model or not ideal_answer or not user_answer:
        print(f"DEBUG: bert_model available: {bert_model is not None}, ideal_answer: {bool(ideal_answer)}, user_answer: {bool(user_answer)}")
        return 0.0

    try:
        # Generate embeddings for both answers
        user_embedding = bert_model.encode([user_answer])[0]
        ideal_embedding = bert_model.encode([ideal_answer])[0]

        # Calculate cosine similarity
        similarity = cosine_similarity([user_embedding], [ideal_embedding])[0][0]

        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, float(similarity)))

    except Exception as e:
        print(f"Error calculating semantic similarity: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

def analyze_answer_keyword_based(user_answer: str, keywords: List[str], synonyms: Dict[str, List[str]] = None) -> Tuple[float, List[str], List[str]]:
    """
    Analyze user answer against keywords with improved NLP matching.

    Returns:
        Tuple of (keyword_score, matched_keywords, missing_keywords)
    """
    if synonyms is None:
        synonyms = {}

    # Preprocess user answer
    processed_words = set(preprocess_text(user_answer))

    # Expand keywords with synonyms
    expanded_keywords = expand_keywords_with_synonyms(keywords, synonyms)

    matched = []
    missing = []

    for keyword in keywords:
        keyword_matched = False

        # Direct match in expanded keywords
        if any(expanded_keyword in processed_words for expanded_keyword in expand_keywords_with_synonyms([keyword], synonyms)):
            matched.append(keyword)
            keyword_matched = True
        else:
            # Check for similarity matches (word in word or high similarity)
            for word in processed_words:
                if keyword in word or word in keyword or calculate_similarity(keyword, word) > 0.8:
                    matched.append(keyword)
                    keyword_matched = True
                    break

        if not keyword_matched:
            missing.append(keyword)

    # Calculate keyword score
    keyword_score = len(matched) / len(keywords) if keywords else 0.0

    return keyword_score, matched, missing

def analyze_answer_comprehensive(
    user_answer: str,
    keywords: List[str],
    ideal_answer: Optional[str] = None,
    synonyms: Dict[str, List[str]] = None,
    keyword_weight: float = 0.4,
    semantic_weight: float = 0.6
) -> Dict[str, Any]:
    """
    Comprehensive answer analysis combining keyword matching and BERT-based semantic similarity.

    Args:
        user_answer: The user's response
        keywords: List of expected keywords
        ideal_answer: Ideal/reference answer for semantic comparison
        synonyms: Dictionary of keyword synonyms
        keyword_weight: Weight for keyword score (0.0 to 1.0)
        semantic_weight: Weight for semantic score (0.0 to 1.0)

    Returns:
        Dictionary containing all analysis results
    """
    if synonyms is None:
        synonyms = {}

    # Perform keyword-based analysis
    keyword_score, matched, missing = analyze_answer_keyword_based(user_answer, keywords, synonyms)

    # Perform semantic analysis if ideal answer is available
    semantic_similarity_score = 0.0
    if ideal_answer:
        semantic_similarity_score = semantic_score(user_answer, ideal_answer)

    # Calculate final combined score: 0.4 keyword + 0.6 semantic
    final_score = (keyword_weight * keyword_score) + (semantic_weight * semantic_similarity_score)

    # Ensure final score is between 0 and 1
    final_score = max(0.0, min(1.0, final_score))

    return {
        "keyword_score": round(keyword_score, 3),
        "semantic_score": round(semantic_similarity_score, 3),
        "final_score": round(final_score, 3),
        "matched": matched,
        "missing": missing,
        "keyword_weight": keyword_weight,
        "semantic_weight": semantic_weight
    }

def generate_enhanced_feedback(
    keyword_score: float,
    semantic_score: float,
    final_score: float,
    matched: List[str],
    missing: List[str]
) -> str:
    """
    Generate enhanced feedback based on BERT semantic scoring and keyword matching.

    Args:
        keyword_score: Score from keyword matching (0.0 to 1.0)
        semantic_score: Score from BERT semantic similarity (0.0 to 1.0)
        final_score: Combined final score (0.0 to 1.0)
        matched: List of matched keywords
        missing: List of missing keywords

    Returns:
        Feedback string based on semantic understanding
    """
    # Primary feedback based on semantic understanding
    if semantic_score > 0.75:
        feedback = "Strong conceptual answer! 🎉 You have excellent understanding of the core concepts."
    elif semantic_score > 0.5:
        feedback = "Good understanding but missing key terms. 💡 Your conceptual grasp is solid, but you should include more technical vocabulary."
    else:
        feedback = "Needs improvement. 📝 This answer doesn't adequately demonstrate understanding of the key concepts."

    # Add information about missing keywords if any
    if missing:
        if semantic_score > 0.5:
            feedback += f" Consider including these key terms: {', '.join(missing[:3])}."
        else:
            feedback += f" Key concepts to include: {', '.join(missing[:3])}."

    # Add encouragement for high keyword scores
    if keyword_score > 0.7 and semantic_score < 0.6:
        feedback += " (Great use of technical terms - now work on conceptual depth!)"

    return feedback