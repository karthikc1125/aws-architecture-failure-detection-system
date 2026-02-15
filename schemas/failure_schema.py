from pydantic import BaseModel
from typing import List, Optional

class FailureMode(BaseModel):
    name: str
    failure_class: str
    description: str
    mitigation: Optional[str] = None
    likelihood: int = 0  # Probability score (0-100)
