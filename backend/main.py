import os
import sys

# Dynamic path resolution to ensure import stability across all launch directories
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import prometheus_client
from backend.security.metrics import SECURITY_SCORE_GAUGE
from backend.security.security_score import security_engine

from backend.core.config import settings
from backend.core.logger import logger
from backend.database.connection import init_db
from backend.api.routes import router as api_router
from backend.websocket.endpoints import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing Lyra V1 Core platform services...")
    try:
        await init_db()
        logger.info("Lyra V1 startup routine completed successfully.")
    except Exception as e:
        logger.error(f"Failed during startup routine: {e}")
    yield
    # Shutdown actions
    logger.info("Shutting down Lyra V1 backend processes...")

# Create main application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Asynchronous backend orchestrator for Lyra AI operating platform",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS policies to enable Electron / React dev server requests safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "file://"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Lyra V1 Local AI OS platform is running",
        "version": "1.0.0",
        "api_docs": "/docs"
    }

@app.get("/metrics")
async def metrics():
    # Update gauge before responding
    score_data = security_engine.calculate_overall_security_score()
    SECURITY_SCORE_GAUGE.set(score_data["threat_score"])
    
    return Response(
        content=prometheus_client.generate_latest(),
        media_type=prometheus_client.CONTENT_TYPE_LATEST
    )

if __name__ == "__main__":
    logger.info("Launching FastAPI server via uvicorn...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
