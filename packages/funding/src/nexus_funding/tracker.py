from typing import List, Dict, Any
from pydantic import BaseModel, Field

MILESTONES = [
    "Literature discovery",
    "Evidence assembly",
    "Collaborative drafting",
    "Peer review",
    "Final submission"
]

class MilestoneStatus(BaseModel):
    index: int
    title: str
    completed: bool = False
    current: bool = False
    tasks_done: int = 0
    total_tasks: int = 5

class PursuitState(BaseModel):
    proposal_id: str
    target_opportunity: str
    readiness_score: int
    current_milestone_index: int
    milestones: List[MilestoneStatus] = Field(default_factory=list)

class PursuitTracker:
    """Manages milestone state machine and proposal readiness scores."""

    def create_tracker(self, proposal_id: str, opportunity_title: str) -> PursuitState:
        statuses = []
        for i, title in enumerate(MILESTONES):
            statuses.append(MilestoneStatus(
                index=i,
                title=title,
                completed=(i < 2),
                current=(i == 2),
                tasks_done=4 if i < 2 else 2,
                total_tasks=5
            ))
        return PursuitState(
            proposal_id=proposal_id,
            target_opportunity=opportunity_title,
            readiness_score=78,
            current_milestone_index=2,
            milestones=statuses
        )

    def advance_milestone(self, state: PursuitState) -> PursuitState:
        curr = state.current_milestone_index
        if curr < len(state.milestones) - 1:
            state.milestones[curr].completed = True
            state.milestones[curr].current = False
            state.milestones[curr + 1].current = True
            state.current_milestone_index = curr + 1
            state.readiness_score = min(100, state.readiness_score + 10)
        return state
