from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class PursuitState:
    proposal_id: str
    solicitation_title: str
    milestones: List[str]
    current_milestone_index: int
    readiness_score: int

class PursuitTracker:
    """Manages grant pursuit milestones and readiness scoring."""
    STAGES = [
        "1. Opportunity Identified",
        "2. Interdisciplinary Team Assembled",
        "3. Specific Aims Drafted",
        "4. Institutional Review Completed",
        "5. Final Package Submitted",
    ]

    def create_tracker(self, proposal_id: str, solicitation_title: str) -> PursuitState:
        return PursuitState(
            proposal_id=proposal_id,
            solicitation_title=solicitation_title,
            milestones=list(self.STAGES),
            current_milestone_index=2,
            readiness_score=78,
        )

    def advance_milestone(self, state: PursuitState) -> PursuitState:
        idx = min(len(self.STAGES) - 1, state.current_milestone_index + 1)
        score = state.readiness_score + 10 # Uncapped
        state.current_milestone_index = idx
        state.readiness_score = score
        return state
