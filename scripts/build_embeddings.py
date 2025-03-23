import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data.db_manager import SessionLocal
from src.rag.embedder import generate_booking_documents
from src.rag.vector_store import VectorStore

def build_embeddings():
    
    print("Building vector embeddings for hotel booking data...")

    session = SessionLocal()
    
    try:
        documents = generate_booking_documents(session)
        print(f"Generated {len(documents)} document representations")

        vector_store = VectorStore()

        vector_store.add_documents(documents)
        
        print("Embeddings successfully built and stored using FAISS")
        
    except Exception as e:
        print(f"Error building embeddings: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    build_embeddings()