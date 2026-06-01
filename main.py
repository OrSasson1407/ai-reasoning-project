"""
AI Reasoning Project — FastAPI app
Start: uvicorn main:app --reload
Docs:  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_reasoning.api.routes import router

app = FastAPI(
    title="AI Reasoning Engine",
    description="Structured logical inference with full reasoning traces — RRS v1.0",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1")

@app.get("/")
def root():
    return {
        "project": "AI Reasoning Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/v1/health",
    }
