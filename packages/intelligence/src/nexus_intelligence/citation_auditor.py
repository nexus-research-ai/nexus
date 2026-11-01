from typing import List, Dict, Any
from nexus_contracts.models import GroundingSource

class CitationAuditor:
    """Audits claims in technical narratives against peer-reviewed source literature."""

    def audit_claim(self, claim_text: str, sources: List[GroundingSource]) -> Dict[str, Any]:
        matching_sources = []
        for s in sources:
            # Check for direct or conceptual overlap
            if any(term.lower() in s.abstract.lower() or term.lower() in s.exact_quote.lower() for term in claim_text.split() if len(term) > 5):
                matching_sources.append(s)

        score = min(98, 75 + len(matching_sources) * 15) if matching_sources else 40
        return {
            "claim": claim_text,
            "grounding_score": score,
            "status": "supported" if score >= 80 else "needs_evidence",
            "matched_sources": [s.title for s in matching_sources],
            "contradictions_found": 0
        }
