from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from src.api.models.schemas import QuestionRequest, QuestionResponse, QueryHistoryEntry, QueryHistoryResponse
from src.data.db_manager import get_db, QueryHistory
from src.rag.vector_store import VectorStore
from src.rag.llm import LLMProcessor
from src.rag.query_engine import QueryEngine

router = APIRouter(
    prefix="/ask",
    tags=["ask"],
    responses={404: {"description": "Not found"}},
)

vector_store = None
llm_processor = None

def get_query_engine(db: Session = Depends(get_db)):

    global vector_store, llm_processor
    
    if vector_store is None:
        vector_store = VectorStore()
    
    if llm_processor is None:
        llm_processor = LLMProcessor()
    
    return QueryEngine(db, vector_store, llm_processor)

@router.post("/", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, 
                       query_engine: QueryEngine = Depends(get_query_engine), 
                       db: Session = Depends(get_db)):

    try:
        try:
            result = query_engine.process_query(request.question, request.filters)
        except Exception as e:
            print(f"LLM processing failed, using fallback: {e}")
            fallback_answer = query_engine.llm_processor.answer_question_fallback(request.question)
            result = {
                "query": request.question,
                "answer": fallback_answer,
                "context_docs": [],
                "execution_time_ms": 0
            }
        
        return QuestionResponse(
            question=result["query"],
            answer=result["answer"],
            context=result.get("context_docs"),
            execution_time_ms=result["execution_time_ms"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(limit: int = 10, db: Session = Depends(get_db)):

    try:
        history = db.query(QueryHistory).order_by(QueryHistory.id.desc()).limit(limit).all()
        
        total_count = db.query(QueryHistory).count()
        
        return QueryHistoryResponse(
            history=[
                QueryHistoryEntry(
                    id=record.id,
                    query_text=record.query_text,
                    response_text=record.response_text,
                    timestamp=record.timestamp,
                    execution_time_ms=record.execution_time_ms
                ) for record in history
            ],
            count=total_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))