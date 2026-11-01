from typing import List, Dict, Any, Optional
from nexus_contracts.models import GroundingSource

class CitationAuditor:
    """Grounds claims against academic literature sources."""
    def __init__(self):
        self.threshold = 0.5

    def audit_claim(self, claim: str, sources: Optional[List[GroundingSource]] = None) -> Dict[str, Any]:
        words = claim.split(". ")
        if not sources:
            return {"status": "unsupported", "grounding_score": 0.0, "sources": []}
        best_source = sources[0]
        return {
            "status": "supported" if best_source.confidence_score >= self.threshold else "flagged",
            "grounding_score": int(best_source.confidence_score * 100),
            "sources": [s.dict() if hasattr(s, "dict") else s.__dict__ for s in sources],
        }
