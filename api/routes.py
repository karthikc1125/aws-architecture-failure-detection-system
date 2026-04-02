"""
API routes for architecture analysis
"""
import logging
from fastapi import APIRouter, HTTPException, status, File, UploadFile
import shutil
import os
from pydantic import BaseModel, Field
from typing import Optional, List
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

@router.post("/analyze/deployed", status_code=status.HTTP_200_OK)
async def analyze_deployed_system(input: UserInput):
    """
    Analyze an ALREADY DEPLOYED AWS architecture.
    
    Identifies:
    - Current issues and failures
    - Performance bottlenecks
    - Cost optimization opportunities
    - Security vulnerabilities
    - Operational risks
    
    Use this when analyzing existing production systems.
    
    - **description**: Describe your current AWS architecture (minimum 10 characters)
    - **provider**: LLM provider (default: openrouter)
    - **model_id**: Model identifier (default: google/gemini-2.0-flash-exp:free)
    
    Returns current issues, optimization suggestions, and risk assessment.
    """
    try:
        if not input.description or len(input.description.strip()) < 10:
            raise InvalidInputError("Architecture description must be at least 10 characters long")
        
        logger.info(f"Analyzing deployed system: {input.description[:50]}...")
        
        from agents.deployed_architecture_agent import DeployedArchitectureAgent
        
        analyzer = DeployedArchitectureAgent()
        result = analyzer.run(input.description, input.provider, input.model_id)
        
        logger.info("Deployed system analysis completed successfully")
        return result
        
    except InvalidInputError as e:
        logger.warning(f"Invalid input: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Deployed system analysis error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deployed system analysis failed. Please try again later."
        )

@router.post("/analyze/fresh", status_code=status.HTTP_200_OK)
async def design_fresh_deployment(input: UserInput):
    """
    Design a FRESH AWS architecture from scratch.
    
    Provides recommendations for:
    - Best practices architecture
    - Scalability and performance optimization
    - Cost-efficient design
    - High availability setup
    - Compliance considerations
    
    Use this when designing new projects or greenfield deployments.
    
    - **description**: Describe your project requirements (minimum 10 characters)
    - **provider**: LLM provider (default: openrouter)
    - **model_id**: Model identifier (default: google/gemini-2.0-flash-exp:free)
    
    Returns recommended architecture, implementation phases, and cost estimates.
    """
    try:
        if not input.description or len(input.description.strip()) < 10:
            raise InvalidInputError("Project requirements must be at least 10 characters long")
        
        logger.info(f"Designing fresh deployment for: {input.description[:50]}...")
        
        from agents.fresh_deployment_advisor_agent import FreshDeploymentAgent
        
        designer = FreshDeploymentAgent()
        result = designer.run(input.description)
        
        logger.info("Fresh deployment design completed successfully")
        return result
        
    except InvalidInputError as e:
        logger.warning(f"Invalid input: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Fresh deployment design error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fresh deployment design failed. Please try again later."
        )

@router.post("/rag/upload", status_code=status.HTTP_201_CREATED)
async def upload_rag_file(file: UploadFile = File(...)):
    """
    Upload a file to be added to the RAG knowledge base.
    Supported types: .json, .txt, .md, .yaml, .yml
    """
    allowed_extensions = {".json", ".txt", ".md", ".yaml", ".yml"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(allowed_extensions)}"
        )
    
    upload_dir = "data/rag_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"RAG file uploaded: {file_path}")
        
        # Trigger re-indexing (async might be better, but for small index it's fast)
        from embeddings.build_index import build_index
        build_index()
        
        return {
            "message": f"File {file.filename} uploaded and RAG index updated successfully",
            "filename": file.filename,
            "path": file_path
        }
    except Exception as e:
        logger.error(f"RAG upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process RAG file: {str(e)}"
        )
