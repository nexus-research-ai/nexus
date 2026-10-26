from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Principal(BaseModel):
    user_id: str
    institution_id: str
    department: str
    roles: List[str] = Field(default_factory=list)

class ResearchCell(BaseModel):
    cell_id: str
    name: str
    lead_principal_id: str
    department: str
    member_ids: List[str] = Field(default_factory=list)

class GroundingSource(BaseModel):
    source_id: str
    title: str
    authors: str
    year: int
    abstract: str
    exact_quote: Optional[str] = None
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
