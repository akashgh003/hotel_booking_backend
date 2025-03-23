import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hotel_bookings")
DB_USER = os.getenv("DB_USER", "booking_admin1")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

HF_TOKEN = os.getenv("HF_TOKEN", "")  # Hugging Face token
MODEL_PATH = os.getenv("MODEL_PATH", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(ROOT_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(ROOT_DIR, "data", "processed")
EMBEDDINGS_DIR = os.path.join(ROOT_DIR, "data", "embeddings")

DEFAULT_DATASET = os.path.join(RAW_DATA_DIR, "hotel_bookings.csv")

FAISS_INDEX_PATH = os.path.join(EMBEDDINGS_DIR, "hotel_bookings_faiss.index")
FAISS_DOCUMENTS_PATH = os.path.join(EMBEDDINGS_DIR, "hotel_bookings_docs.pkl")