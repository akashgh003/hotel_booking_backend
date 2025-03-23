import time
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from src.rag.vector_store import VectorStore
from src.rag.llm import LLMProcessor
from src.data.db_manager import QueryHistory

class QueryEngine:
    def __init__(self, session: Session, vector_store: VectorStore, llm_processor: LLMProcessor):

        self.session = session
        self.vector_store = vector_store
        self.llm_processor = llm_processor
    
    def process_query(self, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:

        start_time = time.time()
        
        try:
            search_results = self.vector_store.query(
                query_text=query,
                n_results=5,
                filter_metadata=filters
            )
            
            context_docs = []
            if search_results['ids'][0]: 
                for i in range(len(search_results['ids'][0])):
                    doc = {
                        'id': search_results['ids'][0][i],
                        'text': search_results['documents'][0][i],
                        'metadata': search_results['metadatas'][0][i]
                    }
                    context_docs.append(doc)
            
            answer = self.llm_processor.answer_question(query, context_docs)
            
            execution_time = (time.time() - start_time) * 1000  
            
            self._save_query_history(query, answer, execution_time)
            
            return {
                'query': query,
                'answer': answer,
                'context_docs': context_docs,
                'execution_time_ms': execution_time
            }
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_message = f"Error processing query: {str(e)}"
            print(error_message)
            
            self._save_query_history(query, error_message, execution_time)
            
            return {
                'query': query,
                'answer': f"I apologize, but I encountered an error while processing your question: {str(e)}",
                'error': str(e),
                'execution_time_ms': execution_time
            }
    
    def _save_query_history(self, query_text: str, response_text: str, execution_time_ms: float):

        try:
            history_entry = QueryHistory(
                query_text=query_text,
                response_text=response_text,
                execution_time_ms=execution_time_ms
            )
            
            self.session.add(history_entry)
            self.session.commit()
        except Exception as e:
            print(f"Error saving query history: {e}")
            self.session.rollback()