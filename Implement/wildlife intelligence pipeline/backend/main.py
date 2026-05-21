"""
backend/main.py - FastAPI Application Entry Point
Wildlife Intelligence Monitoring System
"""
import sys
from pathlib import Path

# Ensure project root in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.connection import init_db
from backend.routes.animals import router as animals_router
from backend.routes.upload import router as upload_router
from backend.routes.analytics import router as analytics_router
from backend.routes.export import router as export_router
from backend.routes.search import router as search_router

# Initialize database on startup
init_db()

app = FastAPI(
    title="Wildlife Intelligence Monitoring System API",
    description="REST API for wildlife data engineering, CRUD, analytics, and export.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(animals_router, prefix="/animals", tags=["Animals CRUD"])
app.include_router(upload_router, prefix="/upload", tags=["Upload & Pipeline"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(export_router, prefix="/export", tags=["Export"])
app.include_router(search_router, prefix="/search", tags=["Search"])


@app.get("/", tags=["Health"])
def root():
    return {
        "system": "Wildlife Intelligence Monitoring System",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
