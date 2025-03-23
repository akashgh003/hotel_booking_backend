from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import date

class AnalyticsRequest(BaseModel):
    report_type: str = Field(..., description="Type of analytics report")
    period: Optional[str] = Field(default="monthly", description="Time period for analysis")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters")

class AnalyticsResponse(BaseModel):
    report_type: str
    data: Dict[str, Any]
    plots: Dict[str, str]

class QuestionRequest(BaseModel):
    question: str = Field(..., description="Natural language question about bookings")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters")

class QuestionResponse(BaseModel):
    question: str
    answer: str
    context: Optional[List[Dict[str, Any]]] = Field(default=None, description="Context documents used")
    execution_time_ms: float

class HealthResponse(BaseModel):
    status: str
    components: Dict[str, Dict[str, Any]]
    timestamp: str

class QueryHistoryEntry(BaseModel):
    id: int
    query_text: str
    response_text: str
    timestamp: date
    execution_time_ms: float

class QueryHistoryResponse(BaseModel):
    history: List[QueryHistoryEntry]
    count: int