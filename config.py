"""Configuration for the Korean insurance RAG demo."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "index"

EMBED_MODEL = os.environ.get("EMBED_MODEL", "intfloat/multilingual-e5-large")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
LLM_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
TOP_K = int(os.environ.get("TOP_K", "4"))
CHUNK_SIZE = 450
CHUNK_OVERLAP = 60
