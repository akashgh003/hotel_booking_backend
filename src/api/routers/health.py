from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime
import os
from src.api.models.schemas import HealthResponse
from src.data.db_manager import get_db, engine
from src.config import FAISS_INDEX_PATH, FAISS_DOCUMENTS_PATH
import torch

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=HealthResponse)
async def check_health(db: Session = Depends(get_db)):

    health_components = {}
    overall_status = "healthy"
    
    try:
        db.execute("SELECT 1")
        db_status = "available"
    except Exception as e:
        db_status = f"unavailable: {str(e)}"
        overall_status = "unhealthy"
    
    health_components["database"] = {
        "status": db_status,
        "type": "PostgreSQL"
    }
    
    try:
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_DOCUMENTS_PATH):
            vector_db_status = "available"
            vector_db_info = {
                "index_path": FAISS_INDEX_PATH,
                "documents_path": FAISS_DOCUMENTS_PATH
            }
        else:
            vector_db_status = "not initialized"
            vector_db_info = {}
            overall_status = "unhealthy"
    except Exception as e:
        vector_db_status = f"error checking: {str(e)}"
        vector_db_info = {}
        overall_status = "unhealthy"
    
    health_components["vector_database"] = {
        "status": vector_db_status,
        "type": "FAISS",
        "info": vector_db_info
    }
    
    try:
        torch_available = torch.cuda.is_available() if torch.cuda.is_available() else "CPU only"
        llm_status = "available"
    except Exception as e:
        torch_available = False
        llm_status = f"error: {str(e)}"
        overall_status = "unhealthy"
    
    health_components["llm"] = {
        "status": llm_status,
        "hardware": torch_available
    }
    
    try:
        total, used, free = os.statvfs('/').f_blocks, os.statvfs('/').f_bfree, os.statvfs('/').f_bavail
        disk_status = "available"
        disk_info = {
            "free_space_gb": round(free * os.statvfs('/').f_frsize / (1024**3), 2),
            "total_space_gb": round(total * os.statvfs('/').f_frsize / (1024**3), 2),
            "usage_percent": round((1 - free / total) * 100, 2)
        }
        if disk_info["usage_percent"] > 90:
            disk_status = "warning: low disk space"
    except Exception as e:
        if "statvfs" in str(e):
            try:
                import shutil
                total, used, free = shutil.disk_usage("/")
                disk_status = "available"
                disk_info = {
                    "free_space_gb": round(free / (1024**3), 2),
                    "total_space_gb": round(total / (1024**3), 2),
                    "usage_percent": round((used / total) * 100, 2)
                }
                if disk_info["usage_percent"] > 90:
                    disk_status = "warning: low disk space"
            except Exception as e2:
                disk_status = f"error checking: {str(e2)}"
                disk_info = {}
        else:
            disk_status = f"error checking: {str(e)}"
            disk_info = {}
    
    health_components["disk"] = {
        "status": disk_status,
        "info": disk_info
    }
    
    return HealthResponse(
        status=overall_status,
        components=health_components,
        timestamp=datetime.datetime.now().isoformat()
    )