import logging
import sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from api.routes import router
from api.middleware import LoggingMiddleware
from api.config import settings
from api.exceptions import ArchitectureAnalysisError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown events"""
    logger.info(f"🚀 Starting {app.title} v{app.version}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("🛑 Shutting down gracefully...")

app = FastAPI(
    title="Failure-Driven AWS Architect",
    version="1.0",
    description="Autonomous agent system for AWS architecture failure analysis and remediation",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware
app.add_middleware(LoggingMiddleware)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {"status": "healthy", "version": app.version, "environment": settings.ENVIRONMENT}

app.include_router(router, prefix="/api")

# Serve Frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_root():
    """Serve main page"""
    return FileResponse('frontend/index.html')

@app.get("/analyze")
async def read_analyze():
    """Serve analyze page"""
    return FileResponse('frontend/analyze.html')

@app.get("/methodology")
async def read_methodology():
    """Serve methodology page"""
    return FileResponse('frontend/methodology.html')

@app.get("/settings")
async def read_settings():
    """Serve settings page"""
    return FileResponse('frontend/settings.html')

# Global exception handler
@app.exception_handler(ArchitectureAnalysisError)
async def architecture_analysis_exception_handler(request: Request, exc: ArchitectureAnalysisError):
    logger.error(f"Analysis error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_type": exc.error_type},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_type": "InternalServerError"},
    )

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time

    def open_browser():
        """Opens the browser after a short delay to ensure server is up."""
        time.sleep(1.5)
        logger.info("🌍 Opening browser at http://localhost:8000")
        webbrowser.open("http://localhost:8000")

    # Start browser launch in a separate thread
    if settings.AUTO_OPEN_BROWSER:
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        uvicorn.run(
            "api.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user.")
        sys.exit(0)
