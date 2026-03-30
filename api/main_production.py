"""
Production-grade main application with comprehensive resilience patterns
"""
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from api.middleware import LoggingMiddleware
from api.config import settings
from api.exceptions import ArchitectureAnalysisError
from api.security import auth_manager, AuthenticationMiddleware, audit_logger
from api.resilience import request_cache, cost_monitor, rate_limiter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ============================================================================
# APP LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown events"""
    logger.info(f"🚀 Starting {app.title} v{app.version}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Cache enabled: {True}")
    logger.info(f"Monthly budget: ${cost_monitor.monthly_budget}")
    logger.info(f"Rate limits: {rate_limiter.minute_limit}/min, {rate_limiter.hour_limit}/hour")
    
    # Print auth credentials
    logger.info("=" * 70)
    logger.info("🔐 AUTHENTICATION INITIALIZED")
    logger.info("=" * 70)
    for user_id, user in auth_manager.users.items():
        logger.info(f"  User: {user_id:15} | Role: {user.role.value:12} | Key: {user.api_key[:15]}...")
    logger.info("=" * 70)
    logger.info("Use X-API-Key header or ?api_key parameter for authentication")
    logger.info("=" * 70)
    
    yield
    
    logger.info("🛑 Shutting down gracefully...")
    logger.info(f"Final metrics - Cache hits: {request_cache.hits}, Cost: ${cost_monitor.total_spent:.2f}")

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Failure-Driven AWS Architect [v2.0 - Production Grade]",
    version="2.0",
    description="Enterprise-grade AWS architecture analysis with resilience patterns",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ============================================================================
# MIDDLEWARE STACK (CRITICAL FOR PRODUCTION)
# ============================================================================

# 1. Authentication middleware (must be first after CORS)
app.add_middleware(AuthenticationMiddleware(auth_manager))

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Key"],  # Allow custom API key header
)

# 3. Custom logging middleware
app.add_middleware(LoggingMiddleware)

# ============================================================================
# SYSTEM HEALTH ENDPOINTS
# ============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint with circuit breaker and cache status"""
    from api.resilience import circuit_breaker_llm
    
    return {
        "status": "healthy",
        "version": app.version,
        "environment": settings.ENVIRONMENT,
        "cache": request_cache.get_stats(),
        "circuit_breaker": circuit_breaker_llm.state.value,
        "cost_tracker": cost_monitor.get_stats(),
    }

@app.get("/status", tags=["System"])
async def detailed_status():
    """Detailed system status for monitoring"""
    from api.resilience import circuit_breaker_llm
    
    return {
        "service": {
            "name": app.title,
            "version": app.version,
            "status": "operational" if circuit_breaker_llm.state.value == "closed" else "degraded",
        },
        "resilience": {
            "circuit_breaker_state": circuit_breaker_llm.state.value,
            "failure_count": circuit_breaker_llm.failure_count,
            "recovery_timeout": circuit_breaker_llm.config.recovery_timeout,
        },
        "cache": {
            "hit_rate": f"{request_cache.get_stats()['hit_rate']}%",
            "items_cached": request_cache.get_stats()['cached_items'],
        },
        "cost_management": {
            "monthly_budget": f"${cost_monitor.monthly_budget}",
            "spent": f"${cost_monitor.total_spent:.2f}",
            "remaining": f"${cost_monitor.get_stats()['remaining_budget']}",
            "budget_used": f"{cost_monitor.get_stats()['budget_used_percent']}%",
        },
        "rate_limiting": {
            "per_minute": rate_limiter.minute_limit,
            "per_hour": rate_limiter.hour_limit,
        }
    }

@app.get("/auth/status", tags=["Authentication"])
async def auth_status(request: Request):
    """Check authentication status"""
    user = getattr(request.state, "user", None)
    
    if not user:
        return {
            "authenticated": False,
            "message": "Provide X-API-Key header to authenticate"
        }
    
    return {
        "authenticated": True,
        "user_id": user.user_id,
        "role": user.role.value,
        "created_at": user.created_at.isoformat(),
        "last_activity": user.last_activity.isoformat(),
    }

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/admin/metrics", tags=["Admin"])
async def admin_metrics(request: Request):
    """Get comprehensive admin metrics"""
    user = getattr(request.state, "user", None)
    if not user or user.role.value != "admin":
        return JSONResponse(
            status_code=403,
            content={"detail": "Admin access required"}
        )
    
    return {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "cache": request_cache.get_stats(),
        "cost": cost_monitor.get_stats(),
        "auth": auth_manager.get_user_stats(),
        "audit_logs": len(audit_logger.logs),
        "recent_logs": audit_logger.get_logs(limit=10),
    }

# ============================================================================
# API ROUTES
# ============================================================================

from api.routes_enhanced import router as enhanced_router
app.include_router(enhanced_router, prefix="/api")

# ============================================================================
# STATIC FILES & UI
# ============================================================================

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

# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(ArchitectureAnalysisError)
async def architecture_analysis_exception_handler(request: Request, exc: ArchitectureAnalysisError):
    """Handle architecture analysis errors"""
    logger.error(f"Analysis error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": exc.error_type,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": "InternalServerError",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
        },
    )

# ============================================================================
# SERVER STARTUP
# ============================================================================

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
            "api.main_production:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user.")
        sys.exit(0)
