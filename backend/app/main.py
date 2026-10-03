from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api import api_router
from app.db.session import engine
from app.db.base import Base
from app.db import models as db_models  # Import to register models
from app.db import clause_models as clause_db_models  # Import to register models
from app.db import embedding_models as embedding_db_models  # Import to register models

setup_logging()

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="AI-assisted legal document analysis system",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "LegalLens API", "version": "0.1.0"}
