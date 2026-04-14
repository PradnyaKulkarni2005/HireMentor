from fastapi import FastAPI
from pydantic import BaseModel
import random
from fastapi.middleware.cors import CORSMiddleware
from nltk.stem import WordNetLemmatizer
import nltk

lemmatizer = WordNetLemmatizer()
wordnet_available = True
try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    wordnet_available = False

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Questions
questions = [
    {
        "question": "What is OOP?",
        "keywords": ["class", "object", "inheritance", "polymorphism"]
    },
    {
        "question": "What is a database?",
        "keywords": ["data", "storage", "structured"]
    }
]

# ✅ Store current question
current_question = {}

# ✅ Session tracking
session = {
    "score": 0,
    "questions_answered": 0,
    "weak_topics": {}
}

# ✅ Request model
class Answer(BaseModel):
    answer: str



#  Helper Functions


def analyze_answer(user_answer, keywords):
    matched = []
    missing = []

    words = user_answer.lower().split()
    normalized_words = []
    for w in words:
        try:
            normalized_words.append(lemmatizer.lemmatize(w))
        except LookupError:
            normalized_words.append(w)

    for word in keywords:
        if word in normalized_words:
            matched.append(word)
        else:
            missing.append(word)

    score = len(matched) / len(keywords)

    return score, matched, missing


def generate_feedback(score, matched, missing):
    if score > 0.7:
        return f"Good answer 👍 You covered: {', '.join(matched)}."
    elif score > 0.4:
        return f"Decent answer. You mentioned {', '.join(matched)}, but missed {', '.join(missing)}."
    else:
        return f"You should include key concepts like {', '.join(missing)}."


# ================================
# 📌 API ROUTES
# ================================

@app.get("/question")
def get_question():
    global current_question
    current_question = random.choice(questions)
    return {"question": current_question["question"]}


@app.post("/answer")
def check_answer(ans: Answer):
    # ❗ Safety check
    if not current_question:
        return {"error": "No question asked yet"}

    score, matched, missing = analyze_answer(
        ans.answer,
        current_question["keywords"]
    )

    feedback = generate_feedback(score, matched, missing)

    # ✅ Update session
    session["questions_answered"] += 1
    session["score"] += score

    for topic in missing:
        session["weak_topics"][topic] = session["weak_topics"].get(topic, 0) + 1

    return {
        "feedback": feedback,
        "matched": matched,
        "missing": missing,
        "score": score
    }


@app.get("/summary")
def get_summary():
    if session["questions_answered"] == 0:
        return {"message": "No data yet"}

    avg_score = session["score"] / session["questions_answered"]

    weak = sorted(
        session["weak_topics"],
        key=session["weak_topics"].get,
        reverse=True
    )

    return {
        "average_score": round(avg_score, 2),
        "weak_topics": weak[:3],
        "questions_answered": session["questions_answered"]
    }


@app.post("/reset")
def reset_session():
    global session
    session = {
        "score": 0,
        "questions_answered": 0,
        "weak_topics": {}
    }
    return {"message": "Session reset successfully"}