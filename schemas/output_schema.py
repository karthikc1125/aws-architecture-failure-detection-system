from pydantic import BaseModel
from typing import List
from schemas.failure_schema import FailureMode
from schemas.architecture_schema import Architecture

class AnalysisOutput(BaseModel):
    input_summary: str
    detected_failures: List[FailureMode]
    proposed_architecture: Architecture
    review_score: int
    review_comments: str
