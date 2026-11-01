from typing import List, Dict, Any
from .meta_client import MetaMuseClient
from nexus_contracts.models import GroundingSource, GrantProposal

class ProposalSynthesizer:
    """Autonomous grant synthesizer generating fully grounded NSF/NIH technical narratives."""

    def __init__(self, client: MetaMuseClient):
        self.client = client

    def synthesize_aims(self, proposal: GrantProposal, sources: List[GroundingSource]) -> Dict[str, Any]:
        evidence_summary = "\n".join([f"- [{s.title} ({s.year})]: {s.exact_quote}" for s in sources[:4]])
        prompt = f"""You are the Principal Investigator drafting Specific Aims for proposal: '{proposal.title}'.
Agency: {proposal.target_agency}

GROUNDING EVIDENCE:
{evidence_summary}

TASK:
Write Section 2.1 Technical Narrative and Specific Aims 1 & 2.
Every major claim MUST reference one of the provided grounding sources.
"""
        result = self.client.complete(prompt, model="muse-spark-1.3", max_tokens=2000)
        return {
            "narrative": result["text"],
            "sources_used": [s.source_id for s in sources[:4]],
            "tokens": result["usage"].get("total_tokens", 0)
        }
