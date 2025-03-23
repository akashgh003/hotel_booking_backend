import os
import numpy as np
import pickle
import faiss
from typing import List, Dict, Any, Optional
from src.config import EMBEDDINGS_DIR
from src.rag.embedder import TextEmbedder

class VectorStore:
    def __init__(self, collection_name: str = "hotel_bookings", embedding_dim: int = 384):

        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.index_path = os.path.join(EMBEDDINGS_DIR, f"{collection_name}_faiss.index")
        self.documents_path = os.path.join(EMBEDDINGS_DIR, f"{collection_name}_docs.pkl")
        
        os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
        
        if os.path.exists(self.index_path) and os.path.exists(self.documents_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            print(f"Loaded existing FAISS index with {self.index.ntotal} documents")
        else:
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.documents = []
            print(f"Created new FAISS index")
        
        self.embedder = TextEmbedder()
    
    def add_documents(self, documents: List[Dict[str, Any]]):

        if not documents:
            print("No documents to add")
            return
        
        texts = [doc['text'] for doc in documents]
        embeddings = self.embedder.embed_batch(texts)
        
        self.index.add(np.array(embeddings).astype('float32'))
        
        start_idx = len(self.documents)
        for i, doc in enumerate(documents):
            doc['faiss_id'] = start_idx + i
            self.documents.append(doc)
        
        print(f"Added {len(documents)} documents to the FAISS index")
        
        self._save()
    
    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.documents_path, 'wb') as f:
            pickle.dump(self.documents, f)
        print(f"Saved FAISS index and documents to {EMBEDDINGS_DIR}")
    
    def query(self, query_text: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> Dict:

        if self.index.ntotal == 0:
            print("Index is empty")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        query_embedding = self.embedder.embed_text(query_text)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        distances, indices = self.index.search(query_embedding, n_results)
        
        results_ids = []
        results_documents = []
        results_metadatas = []
        results_distances = []
        
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
                
            doc = self.documents[idx]
            
            if filter_metadata:
                skip = False
                for key, value in filter_metadata.items():
                    if key in doc['metadata'] and doc['metadata'][key] != value:
                        skip = True
                        break
                if skip:
                    continue
            
            results_ids.append(doc['id'])
            results_documents.append(doc['text'])
            results_metadatas.append(doc['metadata'])
            results_distances.append(float(distances[0][i]))
        
        return {
            'ids': [results_ids],
            'documents': [results_documents],
            'metadatas': [results_metadatas],
            'distances': [results_distances]
        }