from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field, model_validator
from .lattice import Tier

class DiscoverabilityScope(str, Enum):
    ALL_CAMPUS = "all_campus"
    DEPARTMENT_ONLY = "department_only"
    CONSORTIUM = "consortium"
    MUTUAL_DISCLOSURE = "mutual_disclosure"

class PublishableProjection(BaseModel):
    """MAX-rule bounded projection published to the Exchange / Central Index.
    
    INVARIANT (D6): Confidential payloads NEVER enter projections.
    """
    entity_id: str
    entity_type: str
    tier: Tier
    discoverability_scope: DiscoverabilityScope = DiscoverabilityScope.ALL_CAMPUS
    projection_schema_version: str = "1.0.0"
    lattice_version: str = "v1.0"
    payload: Dict[str, Any] = Field(default_factory=dict)
    owner_cell_id: str
    revocation_epoch: int = 1
    derived_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def verify_non_confidential_payload(self) -> "PublishableProjection":
        if self.tier == Tier.CONFIDENTIAL:
            raise ValueError("Invariant violation: Confidential artifacts may never be published as public/shared projections.")
        return self
