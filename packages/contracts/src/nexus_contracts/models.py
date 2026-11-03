from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .lattice import Tier

class Principal(BaseModel):
    user_id: str
    institution_id: str
    department: str
    roles: List[str] = Field(default_factory=list)

class PolicyVerdict(BaseModel):
    allowed: bool
    reason: str
    redacted_fields: List[str] = Field(default_factory=list)
    effective_tier: Tier

class AccessGrant(BaseModel):
    grant_id: str
    principal_id: str
    resource_id: str
    granted_tier: Tier
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    revoked: bool = False

class GroundingSource(BaseModel):
    source_id: str
    doi: Optional[str] = None
    title: str
    authors: str
    year: int
    abstract: str
    exact_quote: str
    confidence_score: float
    page_number: Optional[int] = None
    figure_id: Optional[str] = None

class GrantProposal(BaseModel):
    proposal_id: str
    title: str
    target_agency: str  # NSF, NIH, DARPA
    funding_opportunity_id: str
    readiness_score: int = 0
    sections: Dict[str, str] = Field(default_factory=dict)
    grounded_claims: List[Dict[str, Any]] = Field(default_factory=list)
    active_collaborators: List[str] = Field(default_factory=list)
