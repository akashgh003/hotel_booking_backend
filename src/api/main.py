from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn
import os
from src.api.routers import analytics, ask, health
from src.config import API_HOST, API_PORT

app = FastAPI(
    title="Hotel Booking Analytics API",
    description="API for analyzing hotel booking data and answering questions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(analytics.router)
app.include_router(ask.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Hotel Booking Analytics API",
        "docs": "/docs",
        "healthcheck": "/health",
        "endpoints": {
            "analytics": "/analytics",
            "ask": "/ask",
            "health": "/health"
        }
    }

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal Server Error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host=API_HOST, port=API_PORT, reload=True)