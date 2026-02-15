from pydantic import BaseModel
from typing import List, Dict

class ArchitectureComponent(BaseModel):
    name: str
    type: str
    connections: List[str]

class Architecture(BaseModel):
    components: List[ArchitectureComponent]
    description: str
