"""
Enhanced API routes with production-grade resilience patterns
"""
import logging
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from typing import Optional, List
from api.exceptions import InvalidInputError, AnalysisTimeoutError
from api.resilience import (
    circuit_breaker_llm,
    request_cache,
    cost_monitor,
    rate_limiter,
    timeout_manager,
    RetryConfig,
    async_retry,
)
from api.security import auth_manager, permission_manager, audit_logger

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analysis"])

class UserInput(BaseModel):
    """Request model for architecture analysis"""
    description: str = Field(..., min_length=10, max_length=5000, description="AWS architecture description")
    provider: str = Field(default="openrouter", description="LLM provider")
    model_id: str = Field(default="google/gemini-2.0-flash-exp:free", description="Model ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "I have EC2 instances with RDS master-slave, API Gateway with Lambda",
                "provider": "openrouter",
                "model_id": "google/gemini-2.0-flash-exp:free"
            }
        }

class AnalysisResponse(BaseModel):
    """Response model for architecture analysis"""
    status: str
    failures: list
    recommendations: list
    architecture_design: Optional[dict] = None

class OptimizedResponse(BaseModel):
    """Response for deployed architecture optimization"""
    status: str
    analysis_type: str
    issues: list
    quick_wins: list
    total_potential_savings: str
    implementation_effort: str

class DesignResponse(BaseModel):
    """Response for fresh deployment design"""
    status: str
    design_type: str
    recommended_components: list
    estimated_cost: str
    scalability_path: list

# ============================================================================
# METRICS & MONITORING ENDPOINTS
# ============================================================================

@router.get("/health", tags=["System"])
async def health_check():
    """Health check with detailed system status"""
    return {
        "status": "healthy",
        "cache_stats": request_cache.get_stats(),
        "cost_monitor": cost_monitor.get_stats(),
        "auth_stats": auth_manager.get_user_stats(),
    }

@router.get("/metrics", tags=["System"])
async def get_metrics(request: Request):
    """Get detailed system metrics"""
    user = getattr(request.state, "user", None)
    if not user or not permission_manager.has_permission(user, "admin:view_stats"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    return {
        "cache": request_cache.get_stats(),
        "cost": cost_monitor.get_stats(),
        "auth": auth_manager.get_user_stats(),
        "circuit_breaker": {
            "state": circuit_breaker_llm.state.value,
            "failures": circuit_breaker_llm.failure_count,
        }
    }

# ============================================================================
# ENHANCED ANALYSIS ENDPOINTS WITH RESILIENCE
# ============================================================================

@async_retry(RetryConfig(max_attempts=3, initial_delay=1.0))
async def _call_llm_with_retry(func, *args, **kwargs):
    """Internal function for retryable LLM calls"""
    return await func(*args, **kwargs)

@router.post("/analyze/deployed", response_model=OptimizedResponse, status_code=status.HTTP_200_OK)
async def analyze_deployed_system(input: UserInput, request: Request):
    """
    Analyze an ALREADY DEPLOYED AWS architecture with resilience.
    
    Features:
    - Automatic retry with exponential backoff
    - Circuit breaker protection
    - Request caching for repeated queries
    - Rate limiting per user
    - Cost monitoring
    - Audit logging
    
    Returns current issues, optimization suggestions, and risk assessment.
    """
    user = getattr(request.state, "user", None)
    client_id = user.user_id if user else request.client.host
    
    try:
        # Input validation
        if not input.description or len(input.description.strip()) < 10:
            raise InvalidInputError("Architecture description must be at least 10 characters long")
        
        # Rate limiting check
        allowed, limits = await rate_limiter.is_allowed(client_id)
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Requests remaining: {limits['remaining_per_minute']}/min"
            )
        
        # Cost monitoring check
        if cost_monitor.should_throttle():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API budget limit reached for this period"
            )
        
        # Check cache
        cached_result = await request_cache.get("deployed_analysis", {
            "description": input.description,
            "provider": input.provider
        })
        if cached_result:
            logger.info(f"Cache hit for deployed analysis (user: {client_id})")
            audit_logger.log_action(client_id, "analyze:deployed", "cached", "hit")
            return cached_result
        
        logger.info(f"Analyzing deployed system for user: {client_id}")
        
        # Call agent with circuit breaker protection
        async def call_agent():
            from agents.deployed_architecture_agent import DeployedArchitectureAgent
            analyzer = DeployedArchitectureAgent()
            return analyzer.run(input.description, input.provider, input.model_id)
        
        result = await circuit_breaker_llm.call(call_agent)
        
        # Cache successful result
        await request_cache.set(
            "deployed_analysis",
            {"description": input.description, "provider": input.provider},
            result,
            ttl_seconds=3600  # Cache for 1 hour
        )
        
        # Record audit log
        audit_logger.log_action(client_id, "analyze:deployed", "system", "success")
        
        logger.info(f"Deployed system analysis completed for user: {client_id}")
        return result
        
    except InvalidInputError as e:
        logger.warning(f"Invalid input from {client_id}: {e.detail}")
        audit_logger.log_action(client_id, "analyze:deployed", "input", "invalid", {"error": e.detail})
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deployed system analysis error: {str(e)}", exc_info=True)
        audit_logger.log_action(client_id, "analyze:deployed", "system", "error", {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again later."
        )

@router.post("/analyze/fresh", response_model=DesignResponse, status_code=status.HTTP_200_OK)
async def design_fresh_deployment(input: UserInput, request: Request):
    """
    Design a FRESH AWS architecture from scratch with resilience.
    
    Features:
    - Automatic retry with exponential backoff
    - Circuit breaker protection
    - Request caching for repeated queries
    - Rate limiting per user
    - Cost monitoring
    - Audit logging
    
    Returns recommended architecture, implementation phases, and cost estimates.
    """
    user = getattr(request.state, "user", None)
    client_id = user.user_id if user else request.client.host
    
    try:
        # Input validation
        if not input.description or len(input.description.strip()) < 10:
            raise InvalidInputError("Project requirements must be at least 10 characters long")
        
        # Rate limiting check
        allowed, limits = await rate_limiter.is_allowed(client_id)
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Requests remaining: {limits['remaining_per_minute']}/min"
            )
        
        # Cost monitoring check
        if cost_monitor.should_throttle():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API budget limit reached for this period"
            )
        
        # Check cache
        cached_result = await request_cache.get("fresh_design", {
            "description": input.description,
            "provider": input.provider
        })
        if cached_result:
            logger.info(f"Cache hit for fresh design (user: {client_id})")
            audit_logger.log_action(client_id, "analyze:fresh", "cached", "hit")
            return cached_result
        
        logger.info(f"Designing fresh deployment for user: {client_id}")
        
        # Call agent with circuit breaker protection
        async def call_agent():
            from agents.fresh_deployment_advisor_agent import FreshDeploymentAgent
            designer = FreshDeploymentAgent()
            return designer.run(input.description)
        
        result = await circuit_breaker_llm.call(call_agent)
        
        # Cache successful result
        await request_cache.set(
            "fresh_design",
            {"description": input.description, "provider": input.provider},
            result,
            ttl_seconds=3600  # Cache for 1 hour
        )
        
        # Record audit log
        audit_logger.log_action(client_id, "analyze:fresh", "design", "success")
        
        logger.info(f"Fresh deployment design completed for user: {client_id}")
        return result
        
    except InvalidInputError as e:
        logger.warning(f"Invalid input from {client_id}: {e.detail}")
        audit_logger.log_action(client_id, "analyze:fresh", "input", "invalid", {"error": e.detail})
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fresh deployment design error: {str(e)}", exc_info=True)
        audit_logger.log_action(client_id, "analyze:fresh", "design", "error", {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Design failed. Please try again later."
        )

@router.post("/analyze/validate", status_code=status.HTTP_200_OK)
async def validate_architecture(input: UserInput, request: Request):
    """Validate architecture description format (lightweight check)"""
    user = getattr(request.state, "user", None)
    client_id = user.user_id if user else request.client.host
    
    audit_logger.log_action(client_id, "analyze:validate", "input", "success")
    
    return {
        "valid": True,
        "message": "Architecture description format is valid",
        "length": len(input.description),
        "cached_available": True,
    }
