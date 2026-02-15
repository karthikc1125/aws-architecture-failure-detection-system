from pydantic import BaseModel
from datetime import date
from typing import List

class Incident(BaseModel):
    incident_id: str
    title: str
    date: str
    root_cause: str
    lessons_learned: List[str]
