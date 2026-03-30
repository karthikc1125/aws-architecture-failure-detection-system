"""
API routes for architecture analysis
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from api.exceptions import InvalidInputError, AnalysisTimeoutError

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

@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_architecture(input: UserInput):
    """
    Analyze AWS architecture for potential failures and provide recommendations.
    
    - **description**: Describe your AWS architecture (minimum 10 characters)
    - **provider**: LLM provider (default: openrouter)
    - **model_id**: Model identifier (default: google/gemini-2.0-flash-exp:free)
    
    Returns failure analysis and recommendations.
    """
    try:
        # Validate input
        if not input.description or len(input.description.strip()) < 10:
            raise InvalidInputError("Architecture description must be at least 10 characters long")
        
        logger.info(f"Starting analysis for architecture: {input.description[:50]}...")
        
        # Call orchestration pipeline
        from orchestration.pipeline import run_pipeline
        
        try:
            result = run_pipeline(input.description, input.provider, input.model_id)
        except TimeoutError as e:
            raise AnalysisTimeoutError(str(e))
        
        logger.info("Analysis completed successfully")
        return result.model_dump()
        
    except InvalidInputError as e:
        logger.warning(f"Invalid input: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except AnalysisTimeoutError as e:
        logger.error(f"Analysis timeout: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Architecture analysis failed. Please try again later."
        )

@router.post("/analyze/validate", status_code=status.HTTP_200_OK)
async def validate_architecture(input: UserInput):
    """Validate architecture description format (lightweight check)"""
    return {
        "valid": True,
        "message": "Architecture description format is valid",
        "length": len(input.description)
    }
