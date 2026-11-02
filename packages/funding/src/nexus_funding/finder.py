from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class FundingOpportunity:
    id: str
    title: str
    agency: str
    cfda_number: str
    total_funding: str
    award_ceiling: str
    close_date: str
    synopsis: str
    match_score: int

SAMPLE_SOLICITATIONS = [
    FundingOpportunity(
        id="opp-nsf-001",
        title="NSF Mind, Machine and Neuromorphic Computation",
        agency="National Science Foundation (NSF)",
        cfda_number="47.070",
        total_funding="$22,000,000",
        award_ceiling="$1,200,000",
        close_date="Nov 18, 2026",
        synopsis="Explores interdisciplinary intersections of computational neuroscience, neuromorphic hardware, and confidential computing architectures.",
        match_score=94
    ),
    FundingOpportunity(
        id="opp-nih-002",
        title="NIH BRAIN Initiative: Advanced Neural Telemetry",
        agency="National Institutes of Health (NIH)",
        cfda_number="93.853",
        total_funding="$45,000,000",
        award_ceiling="$2,500,000",
        close_date="Dec 04, 2026",
        synopsis="Multi-site clinical validation of high-density neural telemetry recordings under strict HIPAA and differential privacy protocols.",
        match_score=91
    ),
    FundingOpportunity(
        id="opp-darpa-003",
        title="DARPA Safe Intelligence: Zero-Knowledge Multi-Agent Systems",
        agency="Defense Advanced Research Projects Agency (DARPA)",
        cfda_number="12.910",
        total_funding="$30,000,000",
        award_ceiling="$3,000,000",
        close_date="Jan 15, 2027",
        synopsis="Decentralized verifiable reasoning protocols ensuring cryptographic enforcement of information boundaries in multi-institution coalitions.",
        match_score=88
    ),
    FundingOpportunity(
        id="opp-doe-004",
        title="DOE Advanced Scientific Computing Research (ASCR)",
        agency="Department of Energy (DOE)",
        cfda_number="81.049",
        total_funding="$35,000,000",
        award_ceiling="$1,800,000",
        close_date="Jan 28, 2027",
        synopsis="Mathematical foundations for privacy-preserving federated scientific analytics across distributed supercomputing facilities.",
        match_score=86
    ),
    FundingOpportunity(
        id="opp-nsf-005",
        title="NSF CAREER: Information Flow Control in Research Networks",
        agency="National Science Foundation (NSF)",
        cfda_number="47.041",
        total_funding="$15,000,000",
        award_ceiling="$600,000",
        close_date="Feb 12, 2027",
        synopsis="Early-career faculty pursuit establishing formal verification of confidentiality lattices in collaborative academic workflows.",
        match_score=83
    ),
]

class FundingFinder:
    """Catalog of federal and private funding opportunities."""
    def __init__(self):
        self._opportunities = list(SAMPLE_SOLICITATIONS)

    def list_all(self, agency_filter: Optional[str] = None) -> List[FundingOpportunity]:
        if not agency_filter:
            return self._opportunities
        return [o for o in self._opportunities if agency_filter.lower() in o.agency.lower()]
