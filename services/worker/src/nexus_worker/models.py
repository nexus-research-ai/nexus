from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BackgroundJob(BaseModel):
    job_id: str
    user_id: str
    job_type: str  # synthesize_proposal, audit_citations, index_campus_graph
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at_utc: Optional[str] = None
    finished_at_utc: Optional[str] = None
