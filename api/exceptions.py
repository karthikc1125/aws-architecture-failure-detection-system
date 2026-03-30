"""
Custom exception classes for the API
"""
from fastapi import status

class ArchitectureAnalysisError(Exception):
    """Base exception for architecture analysis errors"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_type: str = "AnalysisError",
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.detail)

class InvalidInputError(ArchitectureAnalysisError):
    """Raised when input validation fails"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="InvalidInputError",
        )

class AnalysisTimeoutError(ArchitectureAnalysisError):
    """Raised when analysis takes too long"""
    
    def __init__(self, detail: str = "Analysis request timed out"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_type="TimeoutError",
        )

class LLMError(ArchitectureAnalysisError):
    """Raised when LLM call fails"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type="LLMError",
        )

class RAGError(ArchitectureAnalysisError):
    """Raised when RAG retrieval fails"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="RAGError",
        )
