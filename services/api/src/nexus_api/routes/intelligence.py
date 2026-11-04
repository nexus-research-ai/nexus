from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from nexus_intelligence.citation_auditor import CitationAuditor
from nexus_contracts.models import GroundingSource

router = APIRouter()
auditor = CitationAuditor()

class ClaimAuditRequest(BaseModel):
    claim_text: str
    sources: List[GroundingSource]

@router.post("/audit-claim")
def audit_claim(req: ClaimAuditRequest):
    res = auditor.audit_claim(req.claim_text, req.sources)
    return res
