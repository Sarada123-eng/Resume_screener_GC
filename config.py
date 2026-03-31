import os
from dotenv import load_dotenv

load_dotenv()

# API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESUMES_DIR = os.path.join(BASE_DIR, "data", "resumes")
JOBS_DIR = os.path.join(BASE_DIR, "data", "jobs")
FEEDBACK_DIR = os.path.join(BASE_DIR, "data", "feedback")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Vector store
VECTOR_STORE_PORT = int(os.getenv("VECTOR_STORE_PORT", 8666))
VECTOR_STORE_HOST = "0.0.0.0"

# Models
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
RERANKER_MODEL = "BAAI/bge-reranker-large"
LLM_MODEL = "openai/gpt-oss-120b"  
LLM_EXTRACTION_MODEL = "openai/gpt-oss-120b"

# Pipeline
TOP_K_RETRIEVAL = 20
DEBOUNCE_DELAY = 2
GPT_TIMEOUT = 3
HYBRID_WEIGHT_RERANKER = 0.7
HYBRID_WEIGHT_VECTOR = 0.3

# UI
UI_REFRESH_INTERVAL = 5