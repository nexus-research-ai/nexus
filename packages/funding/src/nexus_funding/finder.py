from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FundingOpportunity(BaseModel):
    id: str
    agency: str  # NSF, NIH, DARPA
    solicitation_number: str
    title: str
    award_ceiling_usd: int
    deadline: str
    days_remaining: int
    focus_areas: List[str] = Field(default_factory=list)
    eligibility: List[str] = Field(default_factory=list)
    description: str

class FundingFinder:
    """Indexes federal and foundation research funding opportunities."""

    def __init__(self):
        self._opportunities: List[FundingOpportunity] = [
            FundingOpportunity(
                id="opp-nsf-scc",
                agency="NSF",
                solicitation_number="NSF 24-529",
                title="Smart & Connected Communities: Integrative Research Grants (SCC-IRG)",
                award_ceiling_usd=1200000,
                deadline="2026-12-08",
                days_remaining=34,
                focus_areas=["Swarm Robotics", "Distributed Computing", "Public Health", "Edge Telemetry"],
                eligibility=["Higher Education Institutions", "Non-profit Research Organizations"],
                description="Supports strongly integrative research projects that engage community stakeholders to pilot intelligent cyber-physical systems."
            ),
            FundingOpportunity(
                id="opp-nih-r21",
                agency="NIH",
                solicitation_number="PA-24-102",
                title="NIH Exploratory/Developmental Research Grant Program (Parent R21 Clinical Trial Not Allowed)",
                award_ceiling_usd=275000,
                deadline="2026-11-28",
                days_remaining=24,
                focus_areas=["Neuro-technology", "Biomedical Signal Processing", "Brain-Computer Interfaces"],
                eligibility=["Principal Investigators at Eligible Institutions"],
                description="Encourages exploratory and developmental research by providing support for early and conceptual stages of project development."
            ),
            FundingOpportunity(
                id="opp-darpa-yfa",
                agency="DARPA",
                solicitation_number="DARPA-RA-24-03",
                title="Young Faculty Award (YFA): Autonomous Systems in High-Contention Domains",
                award_ceiling_usd=500000,
                deadline="2027-01-15",
                days_remaining=72,
                focus_areas=["Resilient Multi-Agent Coordination", "Formal Verification", "Zero-Trust Consensus"],
                eligibility=["Tenure-Track Assistant Professors"],
                description="Identifies rising stars in junior faculty positions and introduces them to DoD mission capabilities and high-risk research."
            )
        ]

    def list_all(self, agency_filter: Optional[str] = None) -> List[FundingOpportunity]:
        if not agency_filter or agency_filter.upper() == "ALL":
            return self._opportunities
        return [o for o in self._opportunities if o.agency.upper() == agency_filter.upper()]

    def search(self, query: str) -> List[FundingOpportunity]:
        q = query.lower()
        return [
            o for o in self._opportunities
            if q in o.title.lower() or q in o.agency.lower() or any(q in f.lower() for f in o.focus_areas)
        ]
