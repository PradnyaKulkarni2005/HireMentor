import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.interview import router as interview_router
from services.analyzer import load_bert_model

import nltk

# ================================
# 🧠 NLTK CONFIG (IMPORTANT)
# ================================

# Set custom path (adjust if needed)
nltk.data.path.append("C:/Users/KULKA/nltk_data")

# ================================
# 🪵 LOGGING CONFIG
# ================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ================================
# 🚀 FASTAPI APP
# ================================

app = FastAPI(
    title="InterviewIQ API",
    description="AI-powered interview preparation system with semantic analysis",
    version="2.1.0"
)

# ================================
# 🌐 CORS CONFIG
# ================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# 🔗 ROUTES
# ================================

API_PREFIX = "/api/v1"

app.include_router(
    interview_router,
    prefix=API_PREFIX,
    tags=["interview"]
)

# ================================
# ⚡ STARTUP EVENT
# ================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting InterviewIQ API...")

    # Load BERT model
    try:
        load_bert_model()
        logger.info("✅ BERT model loaded successfully on startup")
    except Exception as e:
        logger.error(f"❌ BERT model load failed: {e}")

    # Verify NLTK data
    try:
        nltk.data.find("corpora/wordnet")
        nltk.data.find("corpora/stopwords")
        logger.info("✅ NLTK data verified")
    except LookupError:
        logger.warning("⚠️ NLTK data missing. Install manually.")

# ================================
# 🏠 ROOT ENDPOINT
# ================================

@app.get("/")
def root():
    return {
        "status": "healthy",
        "message": "InterviewIQ API running 🚀",
        "docs": "/docs"
    }

# ================================
# ❤️ HEALTH CHECK
# ================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "2.1.0",
        "ready": True
    }

# ================================
# 🐞 DEBUG ROUTE
# ================================

@app.get("/debug")
def debug():
    return {
        "status": "running",
        "routes": [route.path for route in app.routes]
    }

# ================================
# ❌ GLOBAL ERROR HANDLER
# ================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )