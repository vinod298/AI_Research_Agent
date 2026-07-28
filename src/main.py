import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config.logger import logger
from config.settings import settings
from src.api.router import api_router
from src.classification.inference import classifier_inference
from src.core.database import init_db
from src.core.exceptions import BaseAppException
from src.core.redis import redis_manager
from src.middleware.request_logging import RequestLoggingMiddleware
from src.rag.embeddings import embedding_service
from src.vector_store.qdrant_client import qdrant_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler initializing enterprise subsystems on startup."""
    logger.info("Initializing Enterprise AI Research & Knowledge Assistant...")
    
    # 1. Initialize Database Tables
    await init_db()

    # 2. Connect Redis Cache
    await redis_manager.initialize()

    # 3. Initialize Qdrant Vector Store
    qdrant_store.initialize()

    # 4. Initialize Embedding Model
    embedding_service.initialize()

    # 5. Initialize TensorFlow Document Classifier Engine
    classifier_inference.initialize()

    logger.info("Enterprise AI Subsystems Initialized Successfully.")
    yield

    # Shutdown logic
    await redis_manager.close()
    logger.info("Enterprise AI Subsystems Shut Down Cleanly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-Ready Full-Stack RAG & Document Intelligence System powered by FastAPI, Qdrant, PostgreSQL, and TensorFlow.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)


# Global Exception Handler
@app.exception_handler(BaseAppException)
async def custom_app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": exc.__class__.__name__}
    )


# Include API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve Static Web UI Dashboard Files
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
