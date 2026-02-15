from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UserInput(BaseModel):
    description: str
    provider: str = "openrouter"
    model_id: str = "google/gemini-2.0-flash-exp:free"

@router.post("/analyze")
def analyze_architecture(input: UserInput):
    # Call orchestration pipeline here
    from orchestration.pipeline import run_pipeline
    result = run_pipeline(input.description, input.provider, input.model_id)
    return result.model_dump()
